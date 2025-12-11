from typing import Dict, Any, Callable

TOOLS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

def register(name: str):
    def _decorator(fn):
        TOOLS[name] = fn
        return fn
    return _decorator

@register("extract_functions")
def extract_functions(state):
    code = state.get("code", "")
    funcs = []
    for line in code.splitlines():
        t = line.strip()
        if t.startswith("def "):
            fname = t.split("(")[0].replace("def ", "").strip()
            funcs.append(fname)
    return {"functions": funcs}

@register("check_complexity")
def check_complexity(state):
    code = state.get("code", "")
    lines = code.splitlines()
    per_func = {}
    cur = None
    count = 0

    for line in lines:
        t = line.strip()
        if t.startswith("def "):
            if cur is not None:
                per_func[cur] = count
            cur = t.split("(")[0].replace("def ", "").strip()
            count = 0
        else:
            if cur is not None:
                count += 1

    if cur is not None:
        per_func[cur] = count

    scores = {f: max(1, (v // 5) + 1) for f, v in per_func.items()}
    return {"complexity": scores}

@register("detect_issues")
def detect_issues(state):
    code = state.get("code", "")
    issues = []
    for i, line in enumerate(code.splitlines(), start=1):
        if len(line) > 120:
            issues.append({"line": i, "issue": "long_line"})
        if "TODO" in line or "FIXME" in line:
            issues.append({"line": i, "issue": "todo_found"})
    return {"issues": issues, "issues_count": len(issues)}

@register("suggest_improvements")
def suggest_improvements(state):
    issues = state.get("issues", [])
    sug = []
    for it in issues:
        if it["issue"] == "long_line":
            sug.append("Shorten long lines")
        if it["issue"] == "todo_found":
            sug.append("Resolve TODO/FIXME")
    return {"suggestions": list(dict.fromkeys(sug))}

@register("compute_quality")
def compute_quality(state):
    issues = state.get("issues_count", 0)
    comp = state.get("complexity", {})
    avg = sum(comp.values()) / len(comp) if comp else 0
    score = max(0, 100 - issues * 5 - int(avg) * 5)
    return {"quality_score": score}

@register("refactor_code")
def refactor_code(state):
    # Basic refactor: remove TODO/FIXME and shorten obvious long comment markers
    code = state.get("code", "")
    cleaned = (
        code.replace("FIXME", "")
            .replace("TODO", "")
            .replace("very long comment", "short comment")
            .strip()
    )
    # returning "code" will overwrite state["code"]
    return {"code": cleaned, "issues": [], "issues_count": 0}
