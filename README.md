# Mini Workflow Engine (Code Review Mini-Agent)

## Overview
Minimal FastAPI-based workflow engine supporting:
- Nodes as functions that read/modify shared state
- Edges, branching (`cond:key:op:val:true:false`), looping
- Tool registry for node tools
- SQLite persistence for graphs and runs

## How to run (Windows PowerShell)
1. Open PowerShell and go to project folder:
   `cd C:\Users\prani\workflow-engine`

2. Create virtual env (if not done):
   `python -m venv venv`

3. Activate:
   `venv\Scripts\activate`

4. Install:
   `pip install -r requirements.txt`

5. Start server:
   `uvicorn app.main:app --reload --port 8000`

6. Endpoints:
- `POST /graph/create` → body: { nodes, edges, start }
- `POST /graph/run` → body: { graph_id, initial_state }
- `GET /graph/state/{run_id}`
- `GET /graph/list`

### Example flow (Code Review)
Nodes: extract_functions → check_complexity → detect_issues → suggest_improvements → compute_quality
Edge `score` uses `cond:quality_score:gte:80:done:suggest`

