"""Tool definitions for AI function calling."""

from typing import Dict, Any, List


# File operation tools
READ_FILE_TOOL = {
    "name": "read_file",
    "description": "Read the contents of a file. Use this to examine code, configuration files, or any text file.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read. Can be relative or absolute."
            }
        },
        "required": ["file_path"]
    }
}

WRITE_FILE_TOOL = {
    "name": "write_file",
    "description": "Write content to a file. Creates the file if it doesn't exist, overwrites if it does.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to write. Can be relative or absolute."
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file."
            }
        },
        "required": ["file_path", "content"]
    }
}

GLOB_SEARCH_TOOL = {
    "name": "glob_search",
    "description": "Search for files using glob patterns (e.g., '*.py', '**/*.js', 'src/**/*.ts').",
    "input_schema": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "The glob pattern to match files against."
            }
        },
        "required": ["pattern"]
    }
}

GREP_SEARCH_TOOL = {
    "name": "grep_search",
    "description": "Search for text content within files. Useful for finding specific functions, classes, or text patterns.",
    "input_schema": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "The regex pattern to search for."
            },
            "file_pattern": {
                "type": "string",
                "description": "Optional glob pattern to filter files (e.g., '*.py'). Default: all files."
            }
        },
        "required": ["pattern"]
    }
}

# Shell execution tools
EXECUTE_COMMAND_TOOL = {
    "name": "execute_command",
    "description": "Execute a shell command and return its output. Useful for running tests, installing packages, etc.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute."
            },
            "timeout": {
                "type": "integer",
                "description": "Optional timeout in seconds. Default: 30.",
                "default": 30
            }
        },
        "required": ["command"]
    }
}

# Code editing tools
EDIT_FILE_TOOL = {
    "name": "edit_file",
    "description": "Precisely replace text in a file. Find old_text and replace it with new_text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to edit."
            },
            "old_text": {
                "type": "string",
                "description": "The exact text to be replaced. Must match exactly."
            },
            "new_text": {
                "type": "string",
                "description": "The new text to replace with."
            }
        },
        "required": ["file_path", "old_text", "new_text"]
    }
}

INSERT_CODE_TOOL = {
    "name": "insert_code",
    "description": "Insert code at a specific line in a file. Lines are 1-indexed.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file."
            },
            "line_number": {
                "type": "integer",
                "description": "The line number where to insert the code (1-indexed)."
            },
            "code": {
                "type": "string",
                "description": "The code to insert."
            }
        },
        "required": ["file_path", "line_number", "code"]
    }
}

# Web search tool
WEB_SEARCH_TOOL = {
    "name": "web_search",
    "description": "Use Web Search API to perform web searches. Returns search results with titles, URLs, and summaries.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query keywords (required). Maximum 70 characters."
            },
            "search_engine": {
                "type": "string",
                "description": "Search engine code to use. Default: search_std",
                "default": "search_std"
            },
            "count": {
                "type": "integer",
                "description": "Number of results to return (1-50). Default: 10",
                "default": 10
            },
            "search_domain_filter": {
                "type": "string",
                "description": "Domain to filter search results (e.g., 'www.example.com'). Optional."
            },
            "search_recency_filter": {
                "type": "string",
                "description": "Time range filter for search results. Default: noLimit",
                "default": "noLimit"
            },
            "content_size": {
                "type": "string",
                "description": "Summary content size. Default: medium",
                "default": "medium"
            }
        },
        "required": ["query"]
    }
}

# List all tools
ALL_TOOLS = [
    READ_FILE_TOOL,
    WRITE_FILE_TOOL,
    GLOB_SEARCH_TOOL,
    GREP_SEARCH_TOOL,
    EXECUTE_COMMAND_TOOL,
    EDIT_FILE_TOOL,
    INSERT_CODE_TOOL,
    WEB_SEARCH_TOOL,
]


def get_tool_by_name(name: str) -> Dict[str, Any]:
    """
    Get a tool definition by name.

    Args:
        name: The name of the tool

    Returns:
        Tool definition dictionary

    Raises:
        ValueError: If tool name is not found
    """
    for tool in ALL_TOOLS:
        if tool["name"] == name:
            return tool
    raise ValueError(f"Unknown tool: {name}")


def get_tool_names() -> List[str]:
    """
    Get list of all available tool names.

    Returns:
        List of tool names
    """
    return [tool["name"] for tool in ALL_TOOLS]
