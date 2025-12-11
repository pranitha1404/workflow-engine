from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from .models import GraphDef, NodeDef
from .engine import engine
from . import storage

app = FastAPI(title="Mini Workflow Engine")

class CreateGraphPayload(BaseModel):
    nodes: Dict[str, Dict[str, Any]]
    edges: Dict[str, str]
    start: str

class RunPayload(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

@app.on_event("startup")
async def startup():
    storage.init_db()

@app.post("/graph/create")
async def create_graph(p: CreateGraphPayload):
    nodes = [
        NodeDef(name=n, func=v["func"], params=v.get("params", {}))
        for n, v in p.nodes.items()
    ]
    g = GraphDef(nodes=nodes, edges=p.edges, start=p.start)
    gid = engine.create_graph(g)
    return {"graph_id": gid}

@app.post("/graph/run")
async def run_graph(p: RunPayload):
    try:
        run = await engine.run_graph(p.graph_id, p.initial_state)
        return {"run_id": run.run_id, "status": run.status, "state": run.state, "log": run.log}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/graph/state/{run_id}")
async def get_state(run_id: str):
    r = storage.get_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="run not found")
    return r

@app.get("/graph/list")
async def list_graphs():
    ids = storage.list_graph_ids()
    return {"graphs": ids}
# --- Admin endpoints (persistence inspection & management) ---
@app.get("/admin/graphs")
async def admin_list_graphs():
    ids = storage.list_graph_ids()
    graphs = [storage.get_graph(g) for g in ids]
    return {"count": len(graphs), "graphs": graphs}

@app.get("/admin/runs")
async def admin_list_runs():
    runs = storage.list_runs()
    return {"count": len(runs), "runs": runs}

@app.delete("/admin/run/{run_id}")
async def admin_delete_run(run_id: str):
    ok = storage.delete_run(run_id)
    if not ok:
        raise HTTPException(status_code=404, detail="run not found")
    return {"deleted": run_id}
# --- WebSocket: stream run logs live ---
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

@app.websocket("/ws/run/{run_id}")
async def ws_run(run_id: str, websocket: WebSocket):
    await websocket.accept()
    last_idx = 0
    try:
        while True:
            r = storage.get_run(run_id)
            if not r:
                await websocket.send_json({"error": "run not found"})
                await asyncio.sleep(1)
                continue

            logs = r.get("log", [])
            new = logs[last_idx:]
            for entry in new:
                await websocket.send_json({"log": entry})
            last_idx = len(logs)

            if r.get("status") and r.get("status") != "running":
                await websocket.send_json({"status": r.get("status"), "state": r.get("state")})
                break

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        return


# add root redirect so visiting base URL opens docs
from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
async def _root_redirect():
    return RedirectResponse(url="/docs")
