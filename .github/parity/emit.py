"""環境変数の値を 1 行の PARITY-JSON として出す（matrix などの小さな記録用）。

使い方: python3 emit.py <label> VAR [VAR ...]
JSON として読める値は JSON のまま、読めない値は文字列のまま入れる。
"""
import base64, json, os, sys, zlib

label, names = sys.argv[1], sys.argv[2:]
data = {}
for name in names:
    raw = os.environ.get(name)
    try:
        data[name] = json.loads(raw) if raw is not None else None
    except ValueError:
        data[name] = raw
payload = base64.b64encode(zlib.compress(json.dumps(data, sort_keys=True).encode(), 9)).decode()
print(f"PARITY-JSON {label} {payload}")
