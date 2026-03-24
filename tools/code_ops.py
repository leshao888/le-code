"""Code editing tools."""

import os
from pathlib import Path
from typing import Tuple, Optional

from tools.file_ops import read_file, write_file, _resolve_path
from config.settings import settings


def edit_file(file_path: str, old_text: str, new_text: str) -> Tuple[bool, str]:
    """
    Precisely replace text in a file.

    Args:
        file_path: Path to the file
        old_text: The exact text to be replaced
        new_text: The new text to replace with

    Returns:
        Tuple of (success, message)
    """
    try:
        path = _resolve_path(file_path)

        if not path.exists():
            return False, f"File not found: {file_path}"

        # Read current content
        success, content = read_file(file_path)
        if not success:
            return False, content  # content is error message here

        # Check if old_text exists
        if old_text not in content:
            return False, f"Text not found in file. The exact text must match."

        # Count occurrences
        count = content.count(old_text)

        if count > 1:
            return False, f"Text appears {count} times in file. Please be more specific to ensure unique match."

        # Create backup
        _create_backup(path)

        # Replace text
        new_content = content.replace(old_text, new_text, 1)

        # Write back
        success, msg = write_file(file_path, new_content)
        if not success:
            return False, msg

        return True, f"Successfully replaced text in {file_path}"

    except Exception as e:
        return False, f"Error editing file {file_path}: {str(e)}"


def edit_file_regex(file_path: str, pattern: str, replacement: str) -> Tuple[bool, str]:
    """
    Replace text using regex pattern.

    Args:
        file_path: Path to the file
        pattern: Regex pattern to match
        replacement: Replacement string (can use groups)

    Returns:
        Tuple of (success, message)
    """
    import re

    try:
        path = _resolve_path(file_path)

        if not path.exists():
            return False, f"File not found: {file_path}"

        # Read current content
        success, content = read_file(file_path)
        if not success:
            return False, content

        # Compile regex
        regex = re.compile(pattern)

        # Find matches
        matches = list(regex.finditer(content))

        if not matches:
            return False, f"Pattern not found in file."

        if len(matches) > 1:
            return False, f"Pattern matches {len(matches)} locations. Please be more specific."

        # Create backup
        _create_backup(path)

        # Replace using regex
        new_content = regex.sub(replacement, content, count=1)

        # Write back
        success, msg = write_file(file_path, new_content)
        if not success:
            return False, msg

        return True, f"Successfully replaced pattern in {file_path}"

    except re.error as e:
        return False, f"Invalid regex pattern: {str(e)}"
    except Exception as e:
        return False, f"Error editing file {file_path}: {str(e)}"


def insert_code(file_path: str, line_number: int, code: str) -> Tuple[bool, str]:
    """
    Insert code at a specific line in a file.

    Args:
        file_path: Path to the file
        line_number: Line number where to insert (1-indexed)
        code: The code to insert

    Returns:
        Tuple of (success, message)
    """
    try:
        path = _resolve_path(file_path)

        if not path.exists():
            return False, f"File not found: {file_path}"

        # Read current content
        success, content = read_file(file_path)
        if not success:
            return False, content

        # Split into lines
        lines = content.split('\n')

        # Validate line number
        if line_number < 1 or line_number > len(lines) + 1:
            return False, f"Invalid line number. File has {len(lines)} lines."

        # Create backup
        _create_backup(path)

        # Insert code
        if line_number == len(lines) + 1:
            # Append to end
            lines.append(code)
        else:
            # Insert at specific line
            lines.insert(line_number - 1, code)

        # Join back
        new_content = '\n'.join(lines)

        # Write back
        success, msg = write_file(file_path, new_content)
        if not success:
            return False, msg

        return True, f"Successfully inserted code at line {line_number}"

    except Exception as e:
        return False, f"Error inserting code in {file_path}: {str(e)}"


def delete_lines(file_path: str, start_line: int, end_line: int) -> Tuple[bool, str]:
    """
    Delete a range of lines from a file.

    Args:
        file_path: Path to the file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed, inclusive)

    Returns:
        Tuple of (success, message)
    """
    try:
        path = _resolve_path(file_path)

        if not path.exists():
            return False, f"File not found: {file_path}"

        # Read current content
        success, content = read_file(file_path)
        if not success:
            return False, content

        # Split into lines
        lines = content.split('\n')

        # Validate line numbers
        if start_line < 1 or start_line > len(lines):
            return False, f"Invalid start line. File has {len(lines)} lines."

        if end_line < start_line or end_line > len(lines):
            return False, f"Invalid end line."

        # Create backup
        _create_backup(path)

        # Delete lines
        del lines[start_line - 1:end_line]

        # Join back
        new_content = '\n'.join(lines)

        # Write back
        success, msg = write_file(file_path, new_content)
        if not success:
            return False, msg

        return True, f"Successfully deleted lines {start_line}-{end_line}"

    except Exception as e:
        return False, f"Error deleting lines in {file_path}: {str(e)}"


def undo_edit(file_path: str) -> Tuple[bool, str]:
    """
    Undo the last edit by restoring from backup.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (success, message)
    """
    try:
        path = _resolve_path(file_path)
        backup_path = _get_backup_path(path)

        if not backup_path.exists():
            return False, f"No backup found for {file_path}"

        # Read backup
        content = backup_path.read_text(encoding='utf-8')

        # Write back to original
        success, msg = write_file(file_path, content)
        if not success:
            return False, msg

        return True, f"Successfully restored {file_path} from backup"

    except Exception as e:
        return False, f"Error undoing edit: {str(e)}"


def _create_backup(path: Path) -> None:
    """
    Create a backup of a file.

    Args:
        path: Path to the file to backup
    """
    backup_path = _get_backup_path(path)
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        content = path.read_text(encoding='utf-8')
        backup_path.write_text(content, encoding='utf-8')
    except:
        pass  # Backup creation is optional


def _get_backup_path(path: Path) -> Path:
    """
    Get the backup path for a file.

    Args:
        path: Original file path

    Returns:
        Backup file path
    """
    backup_dir = settings.WORKING_DIR / ".le-code-backups"
    backup_file = backup_dir / f"{path.name}.bak"
    return backup_file


def get_function_definition(file_path: str, function_name: str) -> Tuple[bool, str]:
    """
    Find and extract a function definition from a file.

    Args:
        file_path: Path to the file
        function_name: Name of the function

    Returns:
        Tuple of (success, function text or error message)
    """
    try:
        success, content = read_file(file_path)
        if not success:
            return False, content

        lines = content.split('\n')
        function_lines = []
        brace_count = 0
        found = False

        for i, line in enumerate(lines):
            # Look for function definition
            if not found:
                if f'def {function_name}(' in line or f'function {function_name}(' in line:
                    found = True
                    function_lines.append(line)
                    # Count braces for Python/C-like languages
                    brace_count += line.count('{') - line.count('}')
                continue

            if found:
                function_lines.append(line)
                brace_count += line.count('{') - line.count('}')

                # Check if function body is complete
                if brace_count <= 0:
                    break

        if not found:
            return False, f"Function '{function_name}' not found"

        return True, '\n'.join(function_lines)

    except Exception as e:
        return False, f"Error: {str(e)}"
