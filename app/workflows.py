import asyncio
from typing import Dict, Any, Callable

from .tools import TOOLS

# NODE_FUNCTIONS maps node.func name to an async callable (fn(state, params, tools))
async def _call_tool(tool_name: str, state: Dict[str, Any], params: Dict[str, Any], tools: Dict[str, Callable]):
    # we pass state merged with params into the tool function
    fn = tools.get(tool_name)
    if not fn:
        raise KeyError(f"tool not found: {tool_name}")
    # allow sync tools to run safely in executor if needed (here they are light)
    out = fn(state if state is not None else {})
    # tools return dict of updates
    return out

# mapping used by engine: node function name -> async function(state, params, tools)
NODE_FUNCTIONS = {}
def register_node_func(name: str):
    async def wrapper(state, params, tools):
        return await _call_tool(name, state, params, tools)
    NODE_FUNCTIONS[name] = wrapper
    return wrapper

# register all tools available
for t in list(TOOLS.keys()):
    register_node_func(t)
