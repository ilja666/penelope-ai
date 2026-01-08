"""
Penelope Command Line Interface
Provides a comprehensive CLI with subcommands for different operations
"""
import click
import os
import json
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.box import DOUBLE
from rich.table import Table
from dotenv import load_dotenv
from penelope.core.agent import PenelopeAgent
import sys
import importlib.util

load_dotenv()
console = Console()

def _import_crash_logger():
    """Import crash_logger from debug directory"""
    penelope_root = Path(__file__).parent.parent
    debug_path = penelope_root / "debug" / "crash_logger.py"
    spec = importlib.util.spec_from_file_location("crash_logger", debug_path)
    crash_logger_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(crash_logger_module)
    return crash_logger_module.log_crash

log_crash = _import_crash_logger()

def _get_prompt_box():
    """Create styled prompt box"""
    prompt_label = Text("You", style="bold white")
    prompt_box = Panel(
        prompt_label,
        border_style="bright_magenta",
        box=DOUBLE,
        padding=(0, 1),
        width=50,
        height=3,
        style="bright_magenta"
    )
    return prompt_box

# ============================================================================
# MAIN CLI GROUP
# ============================================================================

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Penelope AI Assistant - Command Line Interface"""
    pass

# ============================================================================
# CHAT COMMAND
# ============================================================================

@cli.command()
@click.argument('query', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Start interactive chat mode')
def chat(query, interactive):
    """Chat with Penelope AI Assistant"""
    try:
        agent = PenelopeAgent()
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        return
    
    if query:
        # Single query mode
        response = agent.chat(query)
        console.print(Markdown(response))
        return
    
    if interactive or not query:
        # Interactive mode
        console.print("[bold magenta]Penelope AI Assistant[/] (Type 'exit' to quit)")
        
        while True:
            console.print(_get_prompt_box())
            user_input = input("> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            try:
                with console.status("[bold green]Penelope is thinking..."):
                    response = agent.chat(user_input)
                
                console.print("\n[bold magenta]Penelope:[/]")
                console.print(Markdown(response))
                console.print("-" * 20)
            except Exception as e:
                log_path = log_crash(e, f"Chat Input: {user_input}")
                console.print(f"\n[bold red]Crash gedetecteerd![/] Log opgeslagen in: [cyan]{log_path}[/]")
                console.print(f"[red]{type(e).__name__}: {str(e)}[/]")

# ============================================================================
# IDE COMMANDS
# ============================================================================

@cli.group()
def ide():
    """IDE control commands"""
    pass

@ide.command()
@click.argument('action')
@click.option('--path', '-p', help='Path parameter')
@click.option('--message', '-m', help='Message parameter')
@click.option('--package', help='Package name')
@click.option('--script', help='Script name')
def cursor(action, path, message, package, script):
    """Control Cursor IDE"""
    from penelope.tools.ide_tools import control_cursor
    
    kwargs = {}
    if path:
        kwargs['path'] = path
    if message:
        kwargs['message'] = message
    
    result = control_cursor(action, **kwargs)
    console.print(result)

@ide.command()
@click.argument('action')
@click.option('--path', '-p', help='Path parameter')
@click.option('--command', '-c', help='Command to run')
def vscode(action, path, command):
    """Control Visual Studio Code"""
    from penelope.tools.ide_tools import control_vscode
    
    kwargs = {}
    if path:
        kwargs['path'] = path
    if command:
        kwargs['command'] = command
    
    result = control_vscode(action, **kwargs)
    console.print(result)

@ide.command()
@click.argument('action')
@click.option('--path', '-p', default='.', help='Repository path')
@click.option('--message', '-m', help='Commit message')
@click.option('--files', '-f', help='Files to add')
@click.option('--branch', '-b', help='Branch name')
def git(action, path, message, files, branch):
    """Control Git operations"""
    from penelope.tools.ide_tools import control_git
    
    kwargs = {'path': path}
    if message:
        kwargs['message'] = message
    if files:
        kwargs['files'] = files
    if branch:
        kwargs['branch_name'] = branch
    
    result = control_git(action, **kwargs)
    console.print(result)

# ============================================================================
# ANDROID STUDIO COMMANDS
# ============================================================================

@cli.group()
def android():
    """Android Studio control commands"""
    pass

@android.command()
@click.argument('action')
@click.option('--path', '-p', help='Path parameter')
def studio(action, path):
    """Control Android Studio"""
    from penelope.tools.android_studio_tools import control_android_studio
    
    kwargs = {}
    if path:
        kwargs['path'] = path
    
    result = control_android_studio(action, **kwargs)
    console.print(result)

@android.command()
@click.argument('message')
def gemini(message):
    """Send message to Gemini in Android Studio"""
    from penelope.tools.android_studio_tools import send_message_to_gemini
    
    result = send_message_to_gemini(message)
    console.print(result)

# ============================================================================
# DEVELOPMENT TOOLS COMMANDS
# ============================================================================

@cli.group()
def dev():
    """Development tools commands"""
    pass

@dev.command()
@click.argument('action')
@click.option('--path', '-p', help='Path parameter')
@click.option('--package', help='Package name')
def python(action, path, package):
    """Control Python development tools"""
    from penelope.tools.ide_tools import control_python
    
    kwargs = {}
    if path:
        kwargs['path'] = path
    if package:
        kwargs['package'] = package
    
    result = control_python(action, **kwargs)
    console.print(result)

@dev.command()
@click.argument('action')
@click.option('--path', '-p', default='.', help='Project path')
@click.option('--package', help='Package name')
@click.option('--script', help='Script name')
def npm(action, path, package, script):
    """Control npm/Node.js operations"""
    from penelope.tools.ide_tools import control_npm
    
    kwargs = {'path': path}
    if package:
        kwargs['package'] = package
    if script:
        kwargs['script_name'] = script
    
    result = control_npm(action, **kwargs)
    console.print(result)

# ============================================================================
# SYSTEM COMMANDS
# ============================================================================

@cli.group()
def system():
    """System control commands"""
    pass

@system.command()
@click.argument('app_name')
def open(app_name):
    """Open an application"""
    from penelope.tools.terminal_tools import open_app
    
    result = open_app(app_name)
    console.print(result)

@system.command()
@click.argument('command')
@click.option('--cwd', '-d', help='Working directory')
def run(command, cwd):
    """Run a system command"""
    from penelope.tools.terminal_tools import run_command
    
    result = run_command(command, cwd)
    console.print(result)

# ============================================================================
# INFO COMMANDS
# ============================================================================

@cli.command()
def tools():
    """List all available tools"""
    try:
        agent = PenelopeAgent()
        table = Table(title="Available Penelope Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="green")
        
        # Get system prompt to extract tool info
        prompt = agent.get_system_prompt()
        # Parse tools from prompt (simplified)
        tools_list = [
            ("read_file", "Read file contents"),
            ("write_file", "Write content to file"),
            ("replace_text", "Replace text in file"),
            ("list_dir", "List directory contents"),
            ("run_command", "Run shell command"),
            ("grep_search", "Search for patterns in files"),
            ("search_files", "Search files with regex"),
            ("open_app", "Open Windows applications"),
            ("control_android_studio", "Control Android Studio"),
            ("control_cursor", "Control Cursor IDE"),
            ("control_vscode", "Control VS Code"),
            ("control_git", "Git operations"),
            ("control_python", "Python development tools"),
            ("control_npm", "npm/Node.js operations"),
        ]
        
        for tool_name, description in tools_list:
            table.add_row(tool_name, description)
        
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")

@cli.command()
def info():
    """Show Penelope information"""
    info_table = Table(title="Penelope AI Assistant")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")
    
    info_table.add_row("Version", "1.0.0")
    info_table.add_row("Platform", "Windows")
    info_table.add_row("CLI", "Click-based with subcommands")
    info_table.add_row("Interactive Mode", "Available")
    info_table.add_row("IDE Support", "Android Studio, Cursor, VS Code")
    info_table.add_row("Dev Tools", "Git, Python, npm")
    
    console.print(info_table)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for CLI"""
    cli()

if __name__ == "__main__":
    main()
