import uuid
from typing import Dict, Any

from .models import GraphDef, RunState, NodeDef
from .workflows import NODE_FUNCTIONS
from . import storage

GRAPHS_CACHE: Dict[str, GraphDef] = {}

class SimpleEngine:

    def create_graph(self, graph: GraphDef) -> str:
        gid = graph.id or str(uuid.uuid4())
        graph.id = gid
        graph_obj = {
            "id": gid,
            "nodes": [n.dict() for n in graph.nodes],
            "edges": graph.edges,
            "start": graph.start
        }
        storage.save_graph(gid, graph_obj)
        GRAPHS_CACHE[gid] = graph
        return gid

    def _load_graph(self, graph_id: str) -> GraphDef:
        if graph_id in GRAPHS_CACHE:
            return GRAPHS_CACHE[graph_id]
        gobj = storage.get_graph(graph_id)
        if not gobj:
            return None
        nodes = [NodeDef(**n) for n in gobj["nodes"]]
        g = GraphDef(id=gobj["id"], nodes=nodes, edges=gobj["edges"], start=gobj["start"])
        GRAPHS_CACHE[graph_id] = g
        return g

    async def run_graph(self, graph_id: str, initial_state: Dict[str, Any]):
        g = self._load_graph(graph_id)
        if not g:
            raise ValueError("Graph not found")

        run_id = str(uuid.uuid4())
        run = RunState(run_id=run_id, graph_id=graph_id, state=dict(initial_state))
        storage.save_run(run_id, run.dict())

        current = g.start
        guard = 0

        while True:
            node = next((n for n in g.nodes if n.name == current), None)
            if not node:
                run.status = "completed"
                storage.update_run(run_id, run.dict())
                break

            run.log.append(f"running: {node.name}")

            fn = NODE_FUNCTIONS.get(node.func)
            if not fn:
                run.log.append(f"missing node function: {node.func}")
                run.status = "failed"
                storage.update_run(run_id, run.dict())
                break

            out = await fn(run.state, node.params, __import__("app.tools", fromlist=["TOOLS"]).TOOLS)
            if isinstance(out, dict):
                run.state.update(out)

            storage.update_run(run_id, run.dict())

            nxt = g.edges.get(node.name)
            if not nxt:
                run.status = "completed"
                storage.update_run(run_id, run.dict())
                break

            if isinstance(nxt, str) and nxt.startswith("cond:"):
                # cond:<key>:<op>:<val>:<true_node>:<false_node>
                p = nxt.split(":")
                key = p[1]
                op = p[2]
                val = float(p[3])
                t = p[4]
                f = p[5]
                sval = run.state.get(key, 0)
                ok = False
                if op == "gte":
                    ok = sval >= val
                if op == "lt":
                    ok = sval < val
                current = t if ok else f
            else:
                current = nxt

            guard += 1
            if guard > 200:
                run.status = "failed"
                run.log.append("loop limit exceeded")
                storage.update_run(run_id, run.dict())
                break

        return run

engine = SimpleEngine()
