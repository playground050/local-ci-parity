"""GitHub と Local CI のログから PARITY-JSON を取り出し、違いを Markdown で出す。

使い方:
  python3 compare.py github.log localci.log --meta meta.json \
      --json out.json [--prev previous.json] [--history history.csv] \
      [--known known.json] [--redact TEXT ...] > report.md

仕様として分かっている違い（known.json）は「既知」に分け、それ以外を「要確認」として先に出す。
"""
import argparse, base64, csv, datetime, json, os, re, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
HISTORY_FIELDS = ["date", "unexpected", "known", "differ", "github_only", "local_only", "same", "local_ci_exit"]

# 実行ごとに変わるのが当然で、違いとして数えないもの
VOLATILE = re.compile(
    r"(run_id|run_number|run_attempt|job_id|check_run_id|workflow_sha|retention_days|"
    r"\.id$|_id$|timestamp|started_at|ACTIONS_RUNTIME_URL|ACTIONS_RESULTS_URL|ACTIONS_CACHE_URL|"
    r"ACTIONS_ID_TOKEN_REQUEST_URL|RUNNER_NAME|RUNNER_TRACKING_ID|GITHUB_RUN_|GITHUB_JOB_ID|"
    r"INVOCATION_ID|JOURNAL_STREAM|HOSTNAME|disk_free_gb|mem_gb)",
    re.I,
)
MARK = re.compile(r"PARITY-JSON (\S+) ([A-Za-z0-9+/=]{20,})")
LABELS = {"differ": "値が違う", "github_only": "GitHub にだけある", "local_only": "Local CI にだけある"}


def extract(path):
    """ラベルごとの JSON を返す。読めなかったラベルは "_broken" に理由を入れる。"""
    out, broken = {}, {}
    with open(path, errors="replace") as f:
        for line in f:
            m = MARK.search(line)
            if not m:
                continue
            label, data = m.groups()
            try:
                raw = base64.b64decode(data)
                try:
                    raw = zlib.decompress(raw)  # probe.py は圧縮して出す。workflow 内の小さな出力は無圧縮
                except zlib.error:
                    pass
                out[label] = json.loads(raw)
                broken.pop(label, None)
            except ValueError as e:
                broken[label] = f"読めない（{len(data)} 文字, {e}）"
    if broken:
        out["_broken"] = broken
    return out


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list) and prefix.endswith("env_names"):
        for name in obj:
            yield f"{prefix}[{name}]", "present"
    else:
        yield prefix, obj


def redact(v, words):
    s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    for w in words:
        if w:
            s = s.replace(w, "<redacted>")
    return s


def cell(s, n=70):
    s = s.replace("|", "\\|").replace("\n", " ")
    return (s[: n - 1] + "…") if len(s) > n else (s or '""')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("github_log"); ap.add_argument("localci_log")
    ap.add_argument("--meta"); ap.add_argument("--json"); ap.add_argument("--prev")
    ap.add_argument("--known", help="既知の違いの定義（既定: このスクリプトと同じ場所の known.json）")
    ap.add_argument("--history", help="件数を追記する history.csv")
    ap.add_argument("--redact", nargs="*", default=[])
    a = ap.parse_args()
    gh, lc = extract(a.github_log), extract(a.localci_log)
    meta = json.load(open(a.meta)) if a.meta else {}
    rows, counts = [], {"differ": 0, "github_only": 0, "local_only": 0, "same": 0, "ignored": 0}
    broken = {"github": gh.pop("_broken", {}), "local": lc.pop("_broken", {})}
    # 片方にしかないジョブは項目ごとに並べず、まとめて注意として出す
    for job in sorted(set(gh) & set(lc)):
        x, y = dict(flatten(gh.get(job, {}))), dict(flatten(lc.get(job, {})))
        for key in sorted(set(x) | set(y)):
            if VOLATILE.search(key):
                counts["ignored"] += 1
                continue
            if key in x and key in y:
                if x[key] == y[key]:
                    counts["same"] += 1
                    continue
                kind = "differ"
            else:
                kind = "github_only" if key in x else "local_only"
            counts[kind] += 1
            rows.append({"kind": kind, "key": f"{job}.{key}",
                         "github": redact(x.get(key, "—"), a.redact),
                         "local": redact(y.get(key, "—"), a.redact)})

    missing = {"github_only": sorted(set(gh) - set(lc)), "local_only": sorted(set(lc) - set(gh))}
    rules = load_known(a.known)
    for r in rows:
        rule = classify(r, rules)
        r["known"] = rule["id"] if rule else None
    counts["known"] = sum(1 for r in rows if r["known"])
    counts["unexpected"] = len(rows) - counts["known"]
    result = {"meta": meta, "counts": counts, "missing_jobs": missing, "broken": broken, "rows": rows}
    if a.json:
        json.dump(result, open(a.json, "w"), ensure_ascii=False, indent=1, sort_keys=True)
    if a.history:
        update_history(a.history, result)
    render(result, rules, a.prev)


def load_known(path):
    path = path or os.path.join(HERE, "known.json")
    try:
        rules = json.load(open(path))["rules"]
    except (OSError, KeyError, json.JSONDecodeError):
        return []
    for rule in rules:
        rule["_keys"] = [re.compile(k) for k in rule["keys"]]
        rule["_normalize"] = [(re.compile(p), r) for p, r in rule.get("normalize", [])]
    return rules


def classify(row, rules):
    """当てはまる既知の違いのルールを返す（最初に当てはまったもの）。なければ None。"""
    for rule in rules:
        if rule.get("kinds") and row["kind"] not in rule["kinds"]:
            continue
        if not any(k.match(row["key"]) for k in rule["_keys"]):
            continue
        if rule["_normalize"]:
            def norm(v):
                for p, r in rule["_normalize"]:
                    v = p.sub(r, v)
                return v
            if norm(row["github"]) != norm(row["local"]):
                continue
        return rule
    return None


def update_history(path, result):
    """history.csv に今回の件数を書く。同じ日の行は置き換え、古い形式の列も読み替える。"""
    c, meta = result["counts"], result["meta"]
    date = meta.get("date") or datetime.date.today().isoformat()
    rows = []
    if os.path.exists(path):
        with open(path, newline="") as f:
            rows = [r for r in csv.DictReader(f) if r.get("date") != date]
    rows.append({"date": date, "unexpected": c["unexpected"], "known": c["known"], "differ": c["differ"],
                 "github_only": c["github_only"], "local_only": c["local_only"], "same": c["same"],
                 "local_ci_exit": meta.get("local_ci_exit", "")})
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HISTORY_FIELDS, extrasaction="ignore", restval="")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["date"]))


def table(rows, with_kind=True):
    head = "| 種類 | 項目 | GitHub | Local CI |\n| --- | --- | --- | --- |" if with_kind \
        else "| 項目 | GitHub | Local CI |\n| --- | --- | --- |"
    lines = [head]
    for r in rows:
        kind = f"{LABELS[r['kind']]} | " if with_kind else ""
        lines.append(f"| {kind}`{r['key']}` | {cell(r['github'])} | {cell(r['local'])} |")
    return "\n".join(lines) + "\n"


def render(result, rules, prev_path):
    meta, counts, rows = result["meta"], result["counts"], result["rows"]
    print(f"# Local CI parity report {meta.get('date') or datetime.date.today().isoformat()}\n")
    for k, v in meta.items():
        if k != "date":
            print(f"- {k}: {v}")
    print(f"\n**要確認 {counts['unexpected']}** ／ 既知の違い {counts['known']} ／ 一致 {counts['same']}"
          f"（実行ごとに変わる {counts['ignored']} 項目は除外）\n")
    for side, jobs in result["missing_jobs"].items():
        if jobs:
            print(f"> 注意: {LABELS[side]}ジョブ結果（比較から除外）: {', '.join(jobs)}\n")
    for side, items in result["broken"].items():
        for label, why in items.items():
            print(f"> 注意: {'GitHub' if side == 'github' else 'Local CI'} の `{label}` を読めなかった: {why}\n")

    if prev_path:
        try:
            prev = json.load(open(prev_path))
            key = lambda r: (r["kind"], r["key"], r["github"], r["local"])  # noqa: E731
            old, new = {key(r): r for r in prev["rows"]}, {key(r): r for r in rows}
            added = [new[k] for k in sorted(set(new) - set(old))]
            gone = [old[k] for k in sorted(set(old) - set(new))]
            print(f"## 前回（{prev['meta'].get('date', '?')}）からの変化\n")
            if not added and not gone:
                print("変化なし。\n")
            for title, items in (("新しく出た違い", added), ("解消した違い", gone)):
                if items:
                    print(f"**{title}（{len(items)}）**\n")
                    print(table(items))
        except (OSError, KeyError, json.JSONDecodeError) as e:
            print(f"> 前回の結果を読めなかった: {e}\n")

    unexpected = [r for r in rows if not r["known"]]
    print(f"## 要確認（{len(unexpected)}）\n")
    if unexpected:
        print("既知の違い（`.github/parity/known.json`）に当てはまらないもの。Local CI の不具合か、まだ分類していない違い。\n")
        print(table(unexpected))
    else:
        print("なし。\n")

    known = [r for r in rows if r["known"]]
    if known:
        print(f"## 既知の違い（{len(known)}）\n")
        print("| 理由 | 件数 |\n| --- | --- |")
        by_rule = {}
        for r in known:
            by_rule.setdefault(r["known"], []).append(r)
        for rule in rules:
            items = by_rule.get(rule["id"])
            if items:
                reason = f"[{rule['reason']}]({rule['doc']})" if rule.get("doc") else rule["reason"]
                print(f"| {reason} | {len(items)} |")
        print()
        for rule in rules:
            items = by_rule.get(rule["id"])
            if items:
                print(f"<details><summary>{rule['reason']}（{len(items)}）</summary>\n")
                print(table(items))
                print("</details>\n")

if __name__ == "__main__":
    main()
