"""The calculator tool. Logic is off-limits; its *description* lives in prompts.py."""

from __future__ import annotations

import ast
import operator

from agno.tools import tool

from triage.prompts import CALCULATOR_DESC

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


@tool(description=CALCULATOR_DESC)
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression and return the numeric result."""
    try:
        return str(round(_eval(ast.parse(expression, mode="eval").body), 2))
    except Exception:
        return "ERROR: not a valid arithmetic expression"
