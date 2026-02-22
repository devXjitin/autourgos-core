"""
Core Tool System.

Provides the Tool class and @tool decorator for defining and managing tools.
"""

import inspect
import re
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

# Regex patterns for docstring parsing
_ARGS_PATTERN = re.compile(
    r"(?:Args?|Arguments?|Parameters?):\s*\n((?:\s+\w+.*\n?)+)", re.IGNORECASE
)
_PARAM_PATTERN = re.compile(
    r"\s+(\w+)\s*(?:\([^)]+\))?\s*:\s*(.+?)(?=\n\s+\w+\s*(?:\([^)]+\))?\s*:|$)",
    re.DOTALL,
)
_NUMPY_PATTERN = re.compile(
    r"Parameters\s*\n\s*-+\s*\n((?:.*\n?)+?)(?:\n\s*(?:Returns|Yields|Raises|See Also|Notes|Examples)|\Z)",
    re.IGNORECASE,
)
_NUMPY_PARAM_PATTERN = re.compile(
    r"(\w+)\s*:\s*[^\n]+\n\s+(.+?)(?=\n\w+\s*:|$)", re.DOTALL
)

_TYPE_MAP = {
    str: "str",
    int: "int",
    float: "float",
    bool: "bool",
    list: "list",
    dict: "dict",
    tuple: "tuple",
    set: "set",
    bytes: "bytes",
}


def _convert_type_to_string(param_type: Any) -> str:
    """Convert Python type hints to string representation for tool schema."""
    if param_type is None or param_type == Any:
        return "any"

    if isinstance(param_type, str):
        return param_type.lower()

    type_str = _TYPE_MAP.get(param_type)
    if type_str:
        return type_str

    origin = get_origin(param_type)
    if origin is None:
        return "str"

    if origin is Union:
        args = get_args(param_type)
        for arg in args:
            if arg is not type(None):
                return _convert_type_to_string(arg)
        return "any"

    if origin in (list, List):
        return "list"
    if origin in (dict, Dict):
        return "dict"
    if origin is tuple:
        return "tuple"
    if origin is set:
        return "set"

    return "str"


def _parse_param_docs(func: Callable) -> Dict[str, str]:
    """Extract parameter descriptions from function docstring."""
    docstring = func.__doc__
    if not docstring:
        return {}

    # Google-style
    args_match = _ARGS_PATTERN.search(docstring)
    if args_match:
        args_section = args_match.group(1)
        return {
            match.group(1): re.sub(r"\s+", " ", match.group(2)).strip()
            for match in _PARAM_PATTERN.finditer(args_section)
        }

    # NumPy-style
    numpy_match = _NUMPY_PATTERN.search(docstring)
    if numpy_match:
        params_section = numpy_match.group(1)
        return {
            match.group(1): re.sub(r"\s+", " ", match.group(2)).strip()
            for match in _NUMPY_PARAM_PATTERN.finditer(params_section)
        }

    return {}


class Tool:
    """Represents a callable tool with metadata and schema."""

    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Optional[Dict[str, Dict[str, Any]]] = None,
        return_direct: bool = False,
    ):
        if not name or not isinstance(name, str):
            raise ValueError("Tool name must be a non-empty string")
        if not callable(function):
            raise ValueError("Tool function must be callable")

        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters or {}
        self.return_direct = return_direct

    def run(self, *args, **kwargs) -> Any:
        """Execute the tool's function."""
        return self.function(*args, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "function": self.function,
            "parameters": self.parameters,
            "return_direct": self.return_direct,
        }

    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's schema without the function reference."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "return_direct": self.return_direct,
        }

    def validate_parameters(self, **kwargs) -> List[str]:
        """Validate provided parameters against the tool's schema."""
        errors = []
        provided = set(kwargs.keys())

        for param_name, param_info in self.parameters.items():
            if param_info.get("required", False) and param_name not in provided:
                errors.append(f"Missing required parameter: {param_name}")

        unexpected = provided - self.parameters.keys()
        if unexpected:
            errors.append(f"Unexpected parameters: {', '.join(unexpected)}")

        return errors

    def __call__(self, *args, **kwargs) -> Any:
        return self.run(*args, **kwargs)

    def __repr__(self) -> str:
        return f"Tool(name='{self.name}', parameters={list(self.parameters.keys())})"

    def __str__(self) -> str:
        return f"Tool '{self.name}': {self.description} ({len(self.parameters)} parameters)"


def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    return_direct: bool = False,
) -> Union[Tool, Callable[[Callable], Tool]]:
    """Decorator to convert a function into a Tool."""

    def decorator(f: Callable) -> Tool:
        tool_name = name or f.__name__
        tool_description = description
        if not tool_description:
            doc = f.__doc__
            tool_description = doc.strip().split("\n", 1)[0].strip() if doc else "No description"

        sig = inspect.signature(f)
        type_hints = get_type_hints(f)
        param_descriptions = _parse_param_docs(f)

        parameters = {
            param_name: {
                "type": _convert_type_to_string(type_hints.get(param_name, Any)),
                "description": param_descriptions.get(
                    param_name, f"The {param_name} parameter"
                ),
                "required": param.default == inspect.Parameter.empty,
            }
            for param_name, param in sig.parameters.items()
            if param.kind
            not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        }

        return Tool(
            name=tool_name,
            description=tool_description,
            function=f,
            parameters=parameters,
            return_direct=return_direct,
        )

    if func is not None:
        return decorator(func)
    return decorator





__all__ = ["Tool", "tool"]
