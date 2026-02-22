# Autourgos Core: Professional-Grade Tool Management

The `autourgos.core` module provides a robust and intuitive system for creating, managing, and integrating tools with AI agents. It is the foundation of the Autourgos Agentic Kit, designed for high-performance, type-safe, and framework-agnostic tool definition.

## Key Features

- **Declarative Tool Creation:** Use the elegant `@tool` decorator to instantly convert Python functions into AI-ready tools.
- **Automatic Schema Generation:** Parameters, type hints, and docstrings are automatically parsed to generate a complete tool schema.
- **Type Safety:** Leverages Python's type hints for robust parameter validation at runtime.
- **Docstring Intelligence:** Automatically extracts tool and parameter descriptions from your function's docstring, supporting Google-style, NumPy-style, and reStructuredText formats.
- **Flexible & Agnostic:** Designed to work with any AI agent or multi-agent system, with zero boilerplate.

## Quickstart: Using the `@tool` Decorator

Creating a tool is as simple as decorating a Python function. The system handles the rest.

```python
from autourgos.core import tool

@tool
def calculator(expression: str) -> str:
    """
    Performs mathematical calculations on a given expression.
    
    Args:
        expression (str): The mathematical expression to evaluate.
    """
    try:
        # Note: eval() is used for demonstration. For production, use a safer alternative.
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

# Example Usage:
# result = calculator("2 + 2 * (3 - 1)")
# print(result)  # Output: 6
```

The `@tool` decorator automatically registers the function with the following metadata:
- **Name:** `calculator`
- **Description:** "Performs mathematical calculations on a given expression."
- **Parameters:** An `expression` of type `str` that is required.

## Advanced Usage: The `Tool` Class

For fine-grained control or dynamic tool creation, you can instantiate the `Tool` class directly.

```python
from autourgos.core import Tool

def web_search(query: str, limit: int = 10) -> str:
    """
    Searches the web for a given query.
    
    Args:
        query (str): The search query to execute.
        limit (int): The maximum number of results to return.
    """
    return f"Simulating search for '{query}' with a limit of {limit} results."

# Manually define the tool
search_tool = Tool(
    name="web_search",
    description="Searches the web for information.",
    function=web_search,
    parameters={
        "query": {"type": "str", "description": "The search query", "required": True},
        "limit": {"type": "int", "description": "Maximum number of results", "required": False},
    }
)

# Example Usage:
# search_results = search_tool.run(query="Autourgos Agentic Kit")
# print(search_results)
```

## Integrating with AI Agents

Once defined, tools can be seamlessly added to any agent that conforms to the Autourgos tool interface.

```python
# Assuming 'agent' is an instance of a Autourgos-compatible AI agent
agent.add_tools(calculator, search_tool)

# The agent can now intelligently invoke these tools based on user input.
# agent.run("What is 5 factorial?")
# agent.run("Find information about Python decorators.")
```

This system empowers developers to build sophisticated and reliable AI applications by providing a clean, powerful, and easy-to-use tool management framework.
