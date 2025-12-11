from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class NodeDef(BaseModel):
    name: str
    func: str
    params: Dict[str, Any] = {}

class GraphDef(BaseModel):
    id: Optional[str] = None
    nodes: List[NodeDef]
    edges: Dict[str, Any]
    start: str

class RunState(BaseModel):
    run_id: str
    graph_id: str
    state: Dict[str, Any]
    log: List[str] = []
    status: str = "running"
