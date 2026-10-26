"""Read-only reuse of numerical function bodies without running app/__init__.py.

The application package initializes Streamlit on import. This research adapter
compiles selected function definitions verbatim in a private namespace. It does
not change their AST, patch sys.modules, modify the source, or run the UI imports.
"""
import ast
import hashlib
import math
from pathlib import Path
from typing import Tuple

import numpy as np
from scipy.optimize import root_scalar

APP = Path(__file__).resolve().parents[2] / "app"
_scope = {"math": math, "np": np, "root_scalar": root_scalar, "Tuple": Tuple}
SOURCE_HASHES = {}


def _load_functions(filename, names):
    path = APP / filename
    source = path.read_bytes()
    SOURCE_HASHES["app/"+filename] = hashlib.sha256(source).hexdigest()
    nodes = [node for node in ast.parse(source, filename=str(path)).body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in nodes} != set(names):
        raise ImportError("Reference calculation changed: review the research adapter.")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), _scope)


_load_functions("cooling_inputs.py", {"finite_number"})
_load_functions("henssge.py", {"cooling_coefficient", "calcola_raffreddamento", "round_to_step_minutes"})
cooling_coefficient = _scope["cooling_coefficient"]
calcola_raffreddamento = _scope["calcola_raffreddamento"]
