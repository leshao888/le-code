"""Shell command execution tools."""

import subprocess
import shlex
import sys
from typing import Tuple, Optional

from config.settings import settings


# Dangerous commands that should not be executed
DANGEROUS_COMMANDS = [
    'rm -rf /',
    'rm -rf /*',
    'dd if=',
    ':(){:|:&};:',  # Fork bomb
    'mkfs',
    'format',
]


def execute_command(command: str, timeout: Optional[int] = None) -> Tuple[bool, str]:
    """
    Execute a shell command safely and return its output.

    Args:
        command: The shell command to execute
        timeout: Optional timeout in seconds (defaults to settings.SHELL_TIMEOUT)

    Returns:
        Tuple of (success, output or error message)
    """
    if timeout is None:
        timeout = settings.SHELL_TIMEOUT

    # Check for dangerous commands
    if _is_dangerous_command(command):
        return False, f"Command blocked for safety: {command}"

    try:
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )

        # Combine stdout and stderr
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"

        # Truncate if too long
        if len(output) > settings.MAX_OUTPUT_LENGTH:
            output = output[:settings.MAX_OUTPUT_LENGTH]
            output += "\n... (output truncated)"

        if result.returncode != 0:
            # Command failed but we still return output
            return True, f"[exit code: {result.returncode}]\n{output}"

        return True, output

    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout} seconds"
    except subprocess.SubprocessError as e:
        return False, f"Error executing command: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def execute_command_interactive(command: str) -> Tuple[bool, str]:
    """
    Execute a command in interactive mode.

    Args:
        command: The shell command to execute

    Returns:
        Tuple of (success, message)
    """
    # Check for dangerous commands
    if _is_dangerous_command(command):
        return False, f"Command blocked for safety: {command}"

    try:
        print(f"\n[Executing: {command}]\n")
        print("-" * 50)

        # Execute command with output going directly to terminal
        result = subprocess.run(
            command,
            shell=True,
            timeout=settings.SHELL_TIMEOUT
        )

        print("-" * 50)

        if result.returncode != 0:
            return False, f"Command exited with code: {result.returncode}"

        return True, "Command completed successfully"

    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {settings.SHELL_TIMEOUT} seconds"
    except KeyboardInterrupt:
        return False, "Command interrupted by user"
    except Exception as e:
        return False, f"Error: {str(e)}"


def _is_dangerous_command(command: str) -> bool:
    """
    Check if a command is potentially dangerous.

    Args:
        command: The command to check

    Returns:
        True if command is dangerous
    """
    command_lower = command.lower().strip()

    # Check against known dangerous patterns
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command_lower:
            return True

    # Additional checks
    if 'rm -rf' in command_lower and 'node_modules' not in command_lower:
        # Allow rm -rf node_modules/ as it's common
        if not any(x in command_lower for x in ['.git', '__pycache__', 'dist', 'build']):
            return True

    return False


def parse_command(command: str) -> Tuple[str, list]:
    """
    Parse a command into base command and arguments.

    Args:
        command: The command string

    Returns:
        Tuple of (base_command, arguments)
    """
    try:
        parts = shlex.split(command)
        if not parts:
            return "", []

        base_cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        return base_cmd, args

    except ValueError:
        # If parsing fails, return the whole command as base
        return command, []


def which(command: str) -> Optional[str]:
    """
    Find the path to a command.

    Args:
        command: The command to find

    Returns:
        Path to the command or None if not found
    """
    try:
        result = subprocess.run(
            ['which', command],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout.strip()

        return None

    except Exception:
        return None
