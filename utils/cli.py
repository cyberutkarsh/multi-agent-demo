from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import time
import random

console = Console()

def print_logo():
    """Print the application logo."""
    logo = """
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║      SUPPLY CHAIN MULTI-AGENT SYSTEM      ║
    ║                                           ║
    ║           Powered by Claude 3.5           ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """
    console.print(Panel(logo, style="bold blue"))

def format_agent_message(message: str):
    """Format and display a message from the agent system."""
    # Simulate typing for a more natural feel
    console.print("\n[bold green]Agent:[/bold green]", end=" ")
    
    # Process markdown and display with typing effect
    for char in message:
        console.print(char, end="", highlight=False)
        time.sleep(0.01 * random.random())
    
    console.print() 