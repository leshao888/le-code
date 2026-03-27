"""Terminal UI components."""

from typing import Optional, Dict, Any, List
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.formatted_text import HTML

from cli.output_formatter import OutputFormatter, default_formatter
from cli.input_handler import InputHandler, default_input_handler
from memory.memory_manager import SessionManager
from config.settings import settings


class TerminalUI:
    """Terminal user interface for le-code."""

    def __init__(self):
        """Initialize the terminal UI."""
        self.formatter = default_formatter
        self.input_handler = default_input_handler
        self.session_manager = SessionManager()
        self._running = True

    def show_welcome(self) -> None:
        """Show welcome message."""
        self.formatter.print_welcome()

    def get_user_input(self) -> Optional[str]:
        """
        Get user input.

        Returns:
            User input or None if exit
        """
        try:
            input_str = self.input_handler.get_input()

            if not input_str:
                return None

            return input_str

        except (KeyboardInterrupt, EOFError):
            self._running = False
            return None

    def display_message(self, role: str, content: str) -> None:
        """
        Display a message.

        Args:
            role: Message role
            content: Message content
        """
        self.formatter.print_message(role, content)

    def display_assistant_response(self, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Display assistant response.

        Args:
            content: Response content
            tool_calls: Optional list of tool calls
        """
        if tool_calls:
            for tool_call in tool_calls:
                self.formatter.print_tool_call(
                    tool_call.get("name", "unknown"),
                    tool_call.get("input", {}),
                    tool_call.get("result", "")
                )

        if content:
            self.formatter.print_message("assistant", content)

    def display_error(self, message: str) -> None:
        """
        Display an error message.

        Args:
            message: Error message
        """
        self.formatter.print_error(message)

    def display_warning(self, message: str) -> None:
        """
        Display a warning message.

        Args:
            message: Warning message
        """
        self.formatter.print_warning(message)

    def display_info(self, message: str) -> None:
        """
        Display an info message.

        Args:
            message: Info message
        """
        self.formatter.print_info(message)

    def display_success(self, message: str) -> None:
        """
        Display a success message.

        Args:
            message: Success message
        """
        self.formatter.print_success(message)

    def display_waiting_animation(self) -> None:
        """Display a waiting animation."""
        self.formatter.display_waiting_animation()

    def display_thinking(self, content: str) -> None:
        """Display AI thinking content."""
        self.formatter.display_thinking(content)

    def display_status_update(self, status: str) -> None:
        """Display status update."""
        self.formatter.display_status_update(status)

    def start_streaming(self) -> None:
        """Start streaming output."""
        self.formatter.start_streaming()

    def end_streaming(self) -> None:
        """End streaming output."""
        self.formatter.end_streaming()

    def display_stream_chunk(self, chunk: str) -> None:
        """Display a streaming chunk."""
        self.formatter.display_stream_chunk(chunk)

    def display_code(self, code: str, language: str = "python") -> None:
        """
        Display code with syntax highlighting.

        Args:
            code: Code to display
            language: Programming language
        """
        self.formatter.print_code(code, language)

    def display_file(self, file_path: str, content: str) -> None:
        """
        Display file contents.

        Args:
            file_path: File path
            content: File content
        """
        self.formatter.print_file_content(file_path, content)

    def display_help(self) -> None:
        """Display help information."""
        self.formatter.print_help()

    def display_status(self, status: Dict[str, Any]) -> None:
        """
        Display application status.

        Args:
            status: Status dictionary
        """
        self.formatter.print_status(status)

    def display_sessions(self, sessions: List[Dict[str, Any]]) -> None:
        """
        Display list of sessions.

        Args:
            sessions: List of session dictionaries
        """
        if not sessions:
            self.display_info("No saved sessions found.")
            return

        self.display_info(f"Found {len(sessions)} session(s):\n")

        for i, session in enumerate(sessions, 1):
            session_id = session.get("id", "unknown")
            created = session.get("created", "unknown")[:19] if session.get("created") else "unknown"
            updated = session.get("updated", "unknown")[:19] if session.get("updated") else "unknown"

            print(f"  {i}. [{session_id}]")
            print(f"     Created: {created}")
            print(f"     Updated: {updated}\n")

    def clear_screen(self) -> None:
        """Clear the screen."""
        self.formatter.clear()

    def is_running(self) -> bool:
        """
        Check if the UI is still running.

        Returns:
            True if running
        """
        return self._running

    def stop(self) -> None:
        """Stop the UI."""
        self._running = False

    def confirm_action(self, message: str) -> bool:
        """
        Ask for user confirmation.

        Args:
            message: Confirmation message

        Returns:
            True if user confirms
        """
        try:
            return confirm(message)
        except (KeyboardInterrupt, EOFError):
            return False

    def handle_special_command(self, command: str, args: Dict[str, Any]) -> bool:
        """
        Handle a special command.

        Args:
            command: Command name
            args: Command arguments

        Returns:
            True if command was handled, False to continue normal flow
        """
        if self.input_handler.is_exit_command(command):
            self.stop()
            return True

        elif self.input_handler.is_clear_command(command):
            self.clear_screen()
            return True

        elif self.input_handler.is_help_command(command):
            self.display_help()
            return True

        elif self.input_handler.is_sessions_command(command):
            sessions = self.session_manager.list_sessions()
            self.display_sessions(sessions)
            return True

        elif self.input_handler.is_model_command(command):
            self.display_status({
                "Model": settings.MODEL_NAME,
                "Base URL": settings.BASE_URL,
                "Max Tokens": settings.MAX_TOKENS,
                "Temperature": settings.TEMPERATURE,
            })
            return True

        # Load and save commands need to be handled by the main application
        # as they require access to the conversation memory
        return False


# Create default UI instance
default_ui = TerminalUI()
