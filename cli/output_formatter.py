"""Output formatting for terminal display."""

import threading
import time
from typing import Dict, Any, Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from config.settings import settings


class OutputFormatter:
    """Format and display output to the terminal."""

    def __init__(self):
        """Initialize the output formatter."""
        import sys
        self.console = Console(file=sys.stdout, force_terminal=True)
        self.enable_colors = settings.ENABLE_COLORS
        self.show_tool_calls = settings.SHOW_TOOL_CALLS

        # Streaming and waiting animation state
        self._is_streaming = False
        self._is_waiting = False
        self._stream_content = []
        self._animation_thread = None
        self._stop_animation = threading.Event()

    def print_message(self, role: str, content: str) -> None:
        """
        Print a conversation message.

        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
        """
        if role == "user":
            self._print_user_message(content)
        elif role == "assistant":
            self._print_assistant_message(content)
        elif role == "system":
            self._print_system_message(content)

    def _print_user_message(self, content: str) -> None:
        """Print a user message."""
        self.console.print(Panel(
            Text(content, style="bold cyan"),
            title="[bold]You[/bold]",
            title_align="left",
            border_style="cyan"
        ))

    def _print_assistant_message(self, content: str) -> None:
        """Print an assistant message with markdown rendering."""
        self.console.print()
        self.console.print(Panel(
            Markdown(content),
            title="[bold]AI[/bold]",
            title_align="left",
            border_style="green",
            padding=(0, 1)
        ))
        self.console.print()

    def _print_system_message(self, content: str) -> None:
        """Print a system message."""
        self.console.print(f"[dim italic][System: {content}][/dim italic]")

    def print_tool_call(self, tool_name: str, args: Dict[str, Any], result: str) -> None:
        """
        Print a tool call and its result.

        Args:
            tool_name: Name of the tool called
            args: Arguments passed to the tool
            result: Tool result
        """
        if not self.show_tool_calls:
            return

        # Format tool name
        self.console.print(f"[bold yellow]🔧 {tool_name}[/bold yellow]")

        # Format arguments (truncated if too long)
        args_str = ", ".join(f"{k}={repr(v)[:50]}" for k, v in args.items())
        if len(args_str) > 100:
            args_str = args_str[:100] + "..."
        self.console.print(f"[dim]Arguments: {args_str}[/dim]")

        # Format result
        if result:
            # Try to detect if result is code
            if '\n' in result or len(result) > 100:
                # Show as code block if multi-line or long
                self.console.print(Syntax(result, "python", theme="monokai", line_numbers=False))
            else:
                self.console.print(Text(result, style="dim"))

    def print_error(self, message: str) -> None:
        """
        Print an error message.

        Args:
            message: Error message
        """
        self.console.print(Panel(
            Text(message, style="bold red"),
            title="[bold red]Error[/bold red]",
            title_align="left",
            border_style="red"
        ))

    def print_warning(self, message: str) -> None:
        """
        Print a warning message.

        Args:
            message: Warning message
        """
        self.console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")

    def print_info(self, message: str) -> None:
        """
        Print an info message.

        Args:
            message: Info message
        """
        self.console.print(f"[dim blue]ℹ️  {message}[/dim blue]")

    def print_success(self, message: str) -> None:
        """
        Print a success message.

        Args:
            message: Success message
        """
        self.console.print(f"[bold green]✓ {message}[/bold green]")

    def print_code(self, code: str, language: str = "python") -> None:
        """
        Print code with syntax highlighting.

        Args:
            code: Code to display
            language: Programming language
        """
        self.console.print()
        self.console.print(Syntax(code, language, theme="monokai", line_numbers=False))
        self.console.print()

    def print_file_content(self, file_path: str, content: str) -> None:
        """
        Print file contents with syntax highlighting.

        Args:
            file_path: Path to the file
            content: File content
        """
        # Detect language from file extension
        ext = file_path.split('.')[-1].lower()
        lang_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'c': 'c',
            'cpp': 'cpp',
            'h': 'c',
            'hpp': 'cpp',
            'go': 'go',
            'rs': 'rust',
            'rb': 'ruby',
            'sh': 'bash',
            'yaml': 'yaml',
            'yml': 'yaml',
            'json': 'json',
            'xml': 'xml',
            'html': 'html',
            'css': 'css',
            'md': 'markdown',
        }
        language = lang_map.get(ext, 'text')

        self.console.print(f"[bold]File: {file_path}[/bold]")
        self.console.print(Syntax(content, language, theme="monokai", line_numbers=False))

    def display_waiting_animation(self) -> None:
        """
        Display animated spinner before AI starts responding.
        Shows a rotating spinner animation.
        """
        self._is_waiting = True
        self._stop_animation.clear()

        def animate():
            spinner_chars = ['◐', '◓', '◑', '◒']
            idx = 0
            while not self._stop_animation.is_set():
                self.console.print(f"\r[cyan]{spinner_chars[idx]} AI thinking...  [0m", end='', markup=False)
                idx = (idx + 1) % len(spinner_chars)
                time.sleep(0.15)
            # Clear the line when done
            self.console.print("\r" + " " * 40 + "\r", end='')

        self._animation_thread = threading.Thread(target=animate, daemon=True)
        self._animation_thread.start()

    def display_thinking(self, content: str) -> None:
        """
        Display AI thinking/thought process.

        Args:
            content: Thinking content to display
        """
        # Stop the waiting animation first
        self._stop_animation.set()
        if self._animation_thread and self._animation_thread.is_alive():
            time.sleep(0.05)

        # Print thinking content with special formatting
        self.console.print(f"\r[dim magenta]💭 Thinking: {content}[0m", end='', markup=False)

    def display_status_update(self, status: str) -> None:
        """
        Display status update (e.g., "searching...", "browsing...").

        Args:
            status: Status message to display
        """
        self.console.print(f"\r[dim yellow]⚡ {status}[0m", end='', markup=False)

    def start_streaming(self) -> None:
        """Start streaming output."""
        # Stop the waiting animation first
        self._stop_animation.set()
        if self._animation_thread and self._animation_thread.is_alive():
            time.sleep(0.05)  # Give it a moment to clear
        self._is_streaming = True
        self._stream_content = []
        # Start AI response with a clean line
        self.console.print()
        self.console.print("[bold green]▶ AI:[/bold green] ", end='', markup=False)

    def end_streaming(self) -> None:
        """End streaming output."""
        self._is_streaming = False
        self._is_waiting = False
        self.console.print()  # New line after streaming

    def display_stream_chunk(self, chunk: str) -> None:
        """
        Display a chunk of streaming text.

        Args:
            chunk: Text chunk to display
        """
        if self._is_streaming and chunk:
            # Use markup=False to prevent Rich from interpreting content as markup
            self.console.print(chunk, end='', markup=False)
            self._stream_content.append(chunk)

    def print_command_output(self, command: str, output: str, exit_code: int) -> None:
        """
        Print command execution output.

        Args:
            command: Command that was executed
            output: Command output
            exit_code: Command exit code
        """
        self.console.print(f"\n[bold yellow]$[/bold yellow] {command}\n")

        if output:
            self.console.print(output, end='')

        if exit_code != 0:
            self.console.print(f"\n[red]Exit code: {exit_code}[/red]")

    def clear(self) -> None:
        """Clear the console."""
        self.console.clear()

    def print_help(self) -> None:
        """Print help information."""
        help_text = """
[bold cyan]le-code - Terminal AI Programming Assistant[/bold cyan]

[bold]Commands:[/bold]
  /help       - Show this help message
  /clear      - Clear conversation history
  /exit       - Exit the application
  /sessions   - List saved sessions
  /save       - Save current session
  /load <id> - Load a session
  /model      - Show current model
  /context    - Show conversation context

[bold]Tips:[/bold]
  - Ask programming questions directly
  - Use natural language for file operations
  - The assistant can read, write, and edit files
  - Commands can be executed with your permission
  - Conversation history is maintained for context

[bold]Model:[/bold] {model}
        """.format(model=settings.MODEL_NAME)

        self.console.print(Markdown(help_text))

    def print_status(self, status: Dict[str, Any]) -> None:
        """
        Print application status.

        Args:
            status: Status dictionary
        """
        self.console.print("\n[bold]Status:[/bold]")
        for key, value in status.items():
            self.console.print(f"  {key}: {value}")
        self.console.print()

    def print_welcome(self) -> None:
        """Print welcome message."""
        welcome = f"""
[bold cyan]╔════════════════════════════════════════╗[/bold cyan]
[bold cyan]║                                      ║[/bold cyan]
[bold cyan]║   [bold white]le-code - Terminal AI Assistant[/bold white]   ║[/bold cyan]
[bold cyan]║                                      ║[/bold cyan]
[bold cyan]║   [dim]Powered by MiniMax-M2.7[/dim]         ║[/bold cyan]
[bold cyan]║                                      ║[/bold cyan]
[bold cyan]╚════════════════════════════════════════╝[/bold cyan]

[bold]Type[/bold] [cyan]/help[/cyan] [bold]for commands[/bold]
[bold]Type[/bold] [cyan]/exit[/cyan] [bold]to quit[/bold]

"""

        self.console.print(welcome)


# Create default formatter instance
default_formatter = OutputFormatter()
