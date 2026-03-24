"""Input handling for user commands."""

from typing import Tuple, Optional, Dict, Any
from pathlib import Path

from config.settings import settings


class InputHandler:
    """Handle user input and special commands."""

    def __init__(self):
        """Initialize the input handler."""
        self.history_file = settings.SESSIONS_DIR / "command_history.txt"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._prompt_session = None

    def _get_prompt_session(self):
        """Lazy initialization of prompt session to handle terminal compatibility."""
        if self._prompt_session is None:
            try:
                from prompt_toolkit import PromptSession
                from prompt_toolkit.history import FileHistory
                from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

                self._prompt_session = PromptSession(
                    history=FileHistory(str(self.history_file)),
                    auto_suggest=AutoSuggestFromHistory(),
                )
            except Exception as e:
                print(f"[Warning: Could not initialize advanced prompt features: {e}]")
                self._prompt_session = False

        return self._prompt_session

    def get_input(self, prompt: str = "> ") -> str:
        """
        Get user input from the terminal.

        Args:
            prompt: Prompt string

        Returns:
            User input string
        """
        try:
            prompt_session = self._get_prompt_session()

            if prompt_session and prompt_session is not False:
                return prompt_session.prompt(prompt)
            else:
                # Fallback to simple input
                return input(prompt)
        except KeyboardInterrupt:
            return "/exit"
        except EOFError:
            return "/exit"

    def parse_input(self, input_str: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Parse user input and identify special commands.

        Args:
            input_str: Raw input string

        Returns:
            Tuple of (is_command, command_name, arguments)
        """
        input_str = input_str.strip()

        if not input_str:
            return False, None, None

        # Check for special commands
        if input_str.startswith('/'):
            return self._parse_command(input_str)

        # Regular input
        return False, None, {"content": input_str}

    def _parse_command(self, command_str: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Parse a special command.

        Args:
            command_str: Command string starting with /

        Returns:
            Tuple of (is_command, command_name, arguments)
        """
        parts = command_str[1:].split(maxsplit=1)
        command_name = parts[0].lower() if parts else ""
        args_str = parts[1] if len(parts) > 1 else ""

        # Map command names
        command_map = {
            'help': 'help',
            'h': 'help',
            '?': 'help',
            'clear': 'clear',
            'c': 'clear',
            'exit': 'exit',
            'quit': 'exit',
            'q': 'exit',
            'sessions': 'sessions',
            's': 'sessions',
            'save': 'save',
            'load': 'load',
            'l': 'load',
            'model': 'model',
            'm': 'model',
            'context': 'context',
            'info': 'context',
        }

        normalized_command = command_map.get(command_name, command_name)

        # Parse arguments
        args = self._parse_command_args(normalized_command, args_str)

        return True, normalized_command, args

    def _parse_command_args(self, command: str, args_str: str) -> Dict[str, Any]:
        """
        Parse command arguments.

        Args:
            command: Command name
            args_str: Arguments string

        Returns:
            Arguments dictionary
        """
        args = {"raw": args_str}

        if command in ['load']:
            # Load command: /load <session_id>
            args["session_id"] = args_str.strip() if args_str else None
        elif command in ['save']:
            # Save command: /save [filename]
            args["filename"] = args_str.strip() if args_str else None
        elif command in ['help', 'clear', 'exit', 'sessions', 'model', 'context']:
            # Commands with no arguments
            pass
        else:
            # Unknown command - treat as raw argument
            args["unknown"] = True

        return args

    def is_exit_command(self, command: Optional[str]) -> bool:
        """
        Check if a command is an exit command.

        Args:
            command: Command name

        Returns:
            True if exit command
        """
        exit_commands = ['exit', 'quit', 'q']
        return command in exit_commands

    def is_clear_command(self, command: Optional[str]) -> bool:
        """
        Check if a command is a clear command.

        Args:
            command: Command name

        Returns:
            True if clear command
        """
        clear_commands = ['clear', 'c']
        return command in clear_commands

    def is_help_command(self, command: Optional[str]) -> bool:
        """
        Check if a command is a help command.

        Args:
            command: Command name

        Returns:
            True if help command
        """
        help_commands = ['help', 'h', '?']
        return command in help_commands

    def is_sessions_command(self, command: Optional[str]) -> bool:
        """
        Check if a command is a sessions command.

        Args:
            command: Command name

        Returns:
            True if sessions command
        """
        sessions_commands = ['sessions', 's']
        return command in sessions_commands

    def is_save_command(self, command: Optional[str]) -> bool:
        """
        Check if a command is a save command.

        Args:
            command: Command name

        Returns:
            True if save command
        """
        save_commands = ['save']
        return command in save_commands

    def is_load_command(self, command: Optional[str]) -> bool:
        """
        Check if a command is a load command.

        Args:
            command: Command name

        Returns:
            True if load command
        """
        load_commands = ['load', 'l']
        return command in load_commands

    def is_model_command(self, command: Optional[str]) -> bool:
        """
        Check if a command is a model command.

        Args:
            command: Command name

        Returns:
            True if model command
        """
        model_commands = ['model', 'm']
        return command in model_commands

    def is_context_command(self, command: Optional[str]) -> bool:
        """
        Check if a command is a context command.

        Args:
            command: Command name

        Returns:
            True if context command
        """
        context_commands = ['context', 'info']
        return command in context_commands


# Create default input handler instance
default_input_handler = InputHandler()
