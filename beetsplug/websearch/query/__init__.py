import re
from typing import Dict
from beetsplug.websearch.gen.models.operation import Operation


def to_beets_query(query: Dict[str, Operation]) -> str:
    return ' '.join([_beets_condition(key, op) for key, op in query.items()])

def _beets_condition(key: str, o: Operation) -> str:
    op = Operation.parse_obj(o)
    if op.contains is not None:
        return f"{key}:{_quote(op.contains)}"
    elif op.eq is not None:
        regex = f"(?i)^{re.escape(op.eq)}$"
        return f"{key}::{_quote(regex)}"
    elif op.regex is not None:
        return f"{key}::{_quote(op.regex)}"
    elif op.gt is not None and op.lt is not None:
        return f"{key}:{_quote(op.gt)}..{_quote(op.lt)}"
    elif op.gt is not None:
        return f"{key}:{_quote(op.gt)}.."
    elif op.lt is not None:
        return f"{key}:..{_quote(op.lt)}"
    raise AssertionError(f"key '{key}' was specified without an operation")

def _quote(v: str) -> str:
    v = v.replace('\\', '\\\\')
    v = v.replace('"', '\\"')
    return f'"{v}"'
