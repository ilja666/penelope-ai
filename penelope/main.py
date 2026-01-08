import click
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.box import DOUBLE
from penelope.core.agent import PenelopeAgent
import sys
import importlib.util
from pathlib import Path

# Import crash_logger from debug directory (hoofddirectory)
def _import_crash_logger():
    """Import crash_logger from debug directory"""
    # Get penelope root directory (parent of penelope/)
    penelope_root = Path(__file__).parent.parent
    debug_path = penelope_root / "debug" / "crash_logger.py"
    spec = importlib.util.spec_from_file_location("crash_logger", debug_path)
    crash_logger_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(crash_logger_module)
    return crash_logger_module.log_crash

log_crash = _import_crash_logger()

load_dotenv()
console = Console()

@click.command()
@click.option('--query', '-q', help='Direct query to Penelope')
@click.option('--interactive', '-i', is_flag=True, help='Start interactive chat mode')
def main(query, interactive):
    """Penelope AI Assistant - CLI Version"""
    
    try:
        agent = PenelopeAgent()
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        return

    if query:
        response = agent.chat(query)
        console.print(Markdown(response))
        return

    console.print("[bold magenta]Penelope AI Assistant[/] (Type 'exit' to quit)")
    
    while True:
        # Create a styled prompt box with pink to red gradient effect
        # Using a rectangular double-line box
        # Create gradient effect by using magenta transitioning to red
        prompt_label = Text("You", style="bold white")
        # Create a box with gradient-like colors (magenta to red)
        prompt_box = Panel(
            prompt_label,
            border_style="bright_magenta",  # Pink/magenta border (start of gradient)
            box=DOUBLE,  # Double line box for rectangular shape
            padding=(0, 1),
            width=50,
            height=3,
            style="bright_magenta"  # Pink background, transitions visually to red
        )
        # Print the prompt box
        console.print(prompt_box)
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

if __name__ == "__main__":
    main()

