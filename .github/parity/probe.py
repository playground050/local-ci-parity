"""runner の環境を調べて、1 行の PARITY-JSON としてログに出す。"""
import base64, json, os, platform, shutil, subprocess, sys, zlib

SECRET_HINTS = ("token", "secret", "password", "key")


def sh(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        out = (r.stdout or r.stderr).strip().splitlines()
        return out[0] if out else ""
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"


def scrub(obj):
    """トークンなどを消す（base64 で出すと GitHub の伏せ字が効かないため）。"""
    if isinstance(obj, dict):
        return {k: ("<removed>" if any(h in k.lower() for h in SECRET_HINTS) else scrub(v))
                for k, v in obj.items() if k != "event"}
    if isinstance(obj, list):
        return [scrub(v) for v in obj]
    return obj


def ctx(name):
    try:
        return scrub(json.loads(os.environ.get(name, "null")))
    except json.JSONDecodeError:
        return "unparseable"


tools = ["git", "python3", "node", "npm", "bash", "curl", "jq", "unzip", "xz", "gcc", "make",
         "docker", "sudo", "ansible", "pip3", "zstd", "rsync", "ssh"]
env_names = sorted(os.environ)
data = {
    "system": {
        "arch": platform.machine(),
        "os_release": sh(". /etc/os-release && echo $PRETTY_NAME"),
        "kernel": platform.release().split("-")[0],
        "user": sh("whoami"),
        "id": sh("id"),
        "nproc": sh("nproc"),
        "mem_gb": sh("awk '/MemTotal/ {printf \"%d\", $2/1024/1024}' /proc/meminfo"),
        "locale": os.environ.get("LANG", ""),
        "timezone": sh("date +%Z"),
        "ulimit_n": sh("ulimit -n"),
        "sudo_nopasswd": sh("sudo -n true && echo yes || echo no"),
        "home": os.environ.get("HOME", ""),
        "workspace": os.environ.get("GITHUB_WORKSPACE", ""),
        "hostedtoolcache": os.path.isdir("/opt/hostedtoolcache"),
        "disk_free_gb": sh("df -BG --output=avail / | tail -1 | tr -dc 0-9"),
    },
    "tools": {t: (sh(f"{t} --version") if shutil.which(t) else None) for t in tools},
    "env_names": env_names,
    "env_github": {k: os.environ[k] for k in env_names
                   if k.startswith(("GITHUB_", "RUNNER_", "CI", "ACTIONS_"))
                   and not any(h in k.lower() for h in SECRET_HINTS)},
    "git": {
        "head": sh("git rev-parse HEAD"),
        "head_matches_github_sha": sh("git rev-parse HEAD") == os.environ.get("GITHUB_SHA"),
        "commit_count": sh("git rev-list --count HEAD"),
        "branch": sh("git rev-parse --abbrev-ref HEAD"),
        "remote": sh("git remote get-url origin"),
        "status_clean": sh("git status --porcelain | wc -l") == "0",
        "last_commit_author": sh("git log -1 --format=%an"),
    },
    "expressions": {k: os.environ.get(k) for k in ("EXPR_SHA", "EXPR_REF_NAME", "EXPR_EVENT")},
    "contexts": {"github": ctx("CTX_GITHUB"), "runner": ctx("CTX_RUNNER"),
                 "job": ctx("CTX_JOB"), "steps": ctx("CTX_STEPS")},
}
label = sys.argv[1] if len(sys.argv) > 1 else "probe"
# Docker は 16KB を超えるログ行を分割するため、圧縮して 1 行を短くする
payload = base64.b64encode(zlib.compress(json.dumps(data, sort_keys=True).encode(), 9)).decode()
print(f"PARITY-JSON {label} {payload}")
