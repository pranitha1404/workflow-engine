import sqlite3, json, pathlib
db = pathlib.Path("workflow.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

data = {"graphs": {}, "runs": {}}

for row in cur.execute("SELECT id, data FROM graphs"):
    gid, gdata = row
    try:
        data["graphs"][gid] = json.loads(gdata)
    except Exception:
        data["graphs"][gid] = gdata

for row in cur.execute("SELECT id, graph_id, status, state, log FROM runs"):
    rid, graph_id, status, state_json, log_json = row
    try:
        state = json.loads(state_json) if state_json else {}
    except Exception:
        state = state_json
    try:
        log = json.loads(log_json) if log_json else []
    except Exception:
        log = log_json
    data["runs"][rid] = {"graph_id": graph_id, "status": status, "state": state, "log": log}

conn.close()

with open("export.json", "w", encoding="utf8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Wrote export.json with", len(data["graphs"]), "graphs and", len(data["runs"]), "runs.")
