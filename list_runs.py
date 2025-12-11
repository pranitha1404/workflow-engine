import sqlite3, pathlib, json
db = pathlib.Path("C:\\Users\\prani\\workflow-engine\\workflow.db")
conn = sqlite3.connect(db)
cur = conn.cursor()
rows = list(cur.execute("SELECT id, graph_id, status FROM runs ORDER BY rowid DESC"))
conn.close()
if not rows:
    print("NO_RUNS")
else:
    for r in rows:
        print(r[0], "| graph:", r[1], "| status:", r[2])
