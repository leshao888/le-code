"""File operation tools implementation."""

import os
import re
import glob as glob_module
from pathlib import Path
from typing import List, Tuple, Optional

from config.settings import settings


def read_file(file_path: str) -> Tuple[bool, str]:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file (relative or absolute)

    Returns:
        Tuple of (success, content or error message)
    """
    try:
        path = _resolve_path(file_path)
        if not path.exists():
            return False, f"File not found: {file_path}"

        if not path.is_file():
            return False, f"Path is not a file: {file_path}"

        # Read file with encoding detection
        try:
            content = path.read_text(encoding='utf-8')
            return True, content
        except UnicodeDecodeError:
            return False, f"Could not decode file {file_path} as UTF-8"

    except Exception as e:
        return False, f"Error reading file {file_path}: {str(e)}"


def write_file(file_path: str, content: str) -> Tuple[bool, str]:
    """
    Write content to a file.

    Args:
        file_path: Path to the file (relative or absolute)
        content: Content to write

    Returns:
        Tuple of (success, message)
    """
    try:
        path = _resolve_path(file_path)

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        path.write_text(content, encoding='utf-8')
        return True, f"Successfully wrote {len(content)} characters to {file_path}"

    except Exception as e:
        return False, f"Error writing file {file_path}: {str(e)}"


def glob_search(pattern: str) -> Tuple[bool, List[str]]:
    """
    Search for files using glob patterns.

    Args:
        pattern: Glob pattern (e.g., '*.py', '**/*.js')

    Returns:
        Tuple of (success, list of file paths or error message)
    """
    try:
        # Use pathlib for better cross-platform support
        path = Path(settings.WORKING_DIR)

        # Convert glob pattern to Path pattern
        # This is a simplified implementation
        matches = list(path.rglob(pattern.replace('**/', '').replace('*', '*')))

        # Filter out directories
        files = [str(f.relative_to(path)) for f in matches if f.is_file()]

        # Limit results to prevent overwhelming output
        if len(files) > 100:
            files = files[:100]

        return True, files

    except Exception as e:
        return False, f"Error searching files: {str(e)}"


def grep_search(pattern: str, file_pattern: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Search for text content within files.

    Args:
        pattern: Regex pattern to search for
        file_pattern: Optional glob pattern to filter files

    Returns:
        Tuple of (success, list of matches or error message)
    """
    try:
        path = Path(settings.WORKING_DIR)
        matches = []

        # Compile regex pattern
        try:
            regex = re.compile(pattern)
        except re.error:
            return False, f"Invalid regex pattern: {pattern}"

        # Find files to search
        if file_pattern:
            files = list(path.rglob(file_pattern.replace('**/', '').replace('*', '*')))
        else:
            files = list(path.rglob('*'))

        # Search in files
        for file_path in files:
            if not file_path.is_file():
                continue

            # Skip binary files
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                # Search for pattern
                for i, line in enumerate(content.split('\n'), 1):
                    if regex.search(line):
                        rel_path = str(file_path.relative_to(path))
                        matches.append(f"{rel_path}:{i}: {line.strip()}")

                        # Limit matches
                        if len(matches) > 100:
                            break

                if len(matches) > 100:
                    break

            except (UnicodeDecodeError, PermissionError):
                continue

        if not matches:
            return True, []

        return True, matches

    except Exception as e:
        return False, f"Error searching content: {str(e)}"


def _resolve_path(file_path: str) -> Path:
    """
    Resolve a file path relative to working directory.

    Args:
        file_path: Path to resolve

    Returns:
        Resolved Path object
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = settings.WORKING_DIR / path
    return path.resolve()


def get_file_info(file_path: str) -> Tuple[bool, dict]:
    """
    Get information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (success, file info dict or error message)
    """
    try:
        path = _resolve_path(file_path)

        if not path.exists():
            return False, {"error": f"File not found: {file_path}"}

        if not path.is_file():
            return False, {"error": f"Path is not a file: {file_path}"}

        stat = path.stat()

        return True, {
            "path": str(path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_text": _is_text_file(path)
        }

    except Exception as e:
        return False, {"error": str(e)}


def _is_text_file(path: Path) -> bool:
    """
    Check if a file is likely a text file.

    Args:
        path: Path to check

    Returns:
        True if likely a text file
    """
    # Common text file extensions
    text_extensions = {
        '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp',
        '.css', '.html', '.json', '.yaml', '.yml', '.xml', '.md',
        '.txt', '.csv', '.log', '.ini', '.cfg', '.conf',
        '.sh', '.bat', '.ps1', '.rb', '.go', '.rs',
    }

    # Check extension
    if path.suffix.lower() in text_extensions:
        return True

    # Try to read a small portion
    try:
        with open(path, 'rb') as f:
            chunk = f.read(1024)
            # Check for null bytes (binary indicator)
            if b'\x00' in chunk:
                return False
            # Check if mostly printable
            text_chars = sum(1 for byte in chunk if 32 <= byte < 127 or byte in b'\n\r\t')
            return text_chars / len(chunk) > 0.7 if chunk else True
    except:
        return False
