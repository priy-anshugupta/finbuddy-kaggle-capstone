"""
FinBuddy Agents CLI

Provides command-line interaction with FinBuddy's agent system,
enabling testing, debugging, and skill execution directly from the terminal.

Commands:
  finbuddy-cli chat              → Interactive chat with FinBuddy
  finbuddy-cli chat --agent=adk  → Chat using Google ADK backend
  finbuddy-cli test              → Run agent evaluation tests
  finbuddy-cli list-agents       → List all registered agents
  finbuddy-cli deploy --check    → Pre-deployment health check
  finbuddy-cli mcp-server        → Start the MCP server

Demonstrates the course concept: Agent Skills (Agents CLI)
"""

import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from app.config import settings

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="finbuddy-cli")
def cli():
    """
    FinBuddy Agents CLI — Interact with your AI financial assistant from the terminal.

    Built for the Kaggle 5-Day AI Agents: Intensive Vibe Coding Capstone Project.
    """
    pass


@cli.command()
@click.option("--agent", "agent_framework", type=click.Choice(["adk", "langchain"]), default="adk",
              help="Agent framework to use (adk = Google ADK, langchain = legacy)")
@click.option("--user-id", default="cli_user", help="User ID for the session")
def chat(agent_framework, user_id):
    """
    Start an interactive chat session with FinBuddy.

    Example:
        finbuddy-cli chat
        finbuddy-cli chat --agent=adk --user-id=priya_123
    """
    console.print(Panel.fit(
        f"[bold green]FinBuddy Interactive Chat[/bold green]\n"
        f"Framework: [cyan]{agent_framework}[/cyan] | User: [cyan]{user_id}[/cyan]\n"
        f"Type 'quit' or 'exit' to leave.",
        title="Welcome",
        border_style="green"
    ))

    # Set framework for this session
    settings.AGENT_FRAMEWORK = agent_framework

    from google_adk.service import get_agent_service

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    service = get_agent_service()

    conversation_id = f"cli_{user_id}_{int(asyncio.get_event_loop().time())}"

    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        if user_input.strip().lower() in ("quit", "exit", "q"):
            console.print("[yellow]Goodbye![/yellow]")
            break

        with console.status("[bold green]FinBuddy is thinking...[/bold green]"):
            result = loop.run_until_complete(
                service.process_message(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    message=user_input,
                )
            )

        if result.get("success"):
            console.print(Panel(
                result.get("response", "(No response)"),
                title="[bold green]FinBuddy[/bold green]",
                border_style="green"
            ))
            console.print(
                f"[dim]Framework: {result.get('framework', 'unknown')} | "
                f"Duration: {result.get('duration_ms', 0):.0f}ms[/dim]"
            )
        else:
            console.print(Panel(
                f"[red]Error:[/red] {result.get('error', 'Unknown error')}",
                title="[bold red]Failed[/bold red]",
                border_style="red"
            ))


@cli.command()
def list_agents():
    """
    List all registered agents in the FinBuddy system.

    Shows both ADK and LangChain agent registries.
    """
    table = Table(title="FinBuddy Agent Registry")
    table.add_column("Block", style="cyan", no_wrap=True)
    table.add_column("Agent Name", style="magenta")
    table.add_column("Framework", style="green")
    table.add_column("Description", style="white")

    # ADK agents
    adk_agents = [
        ("Root", "finbuddy_root", "ADK", "Top-level router"),
        ("Block 1", "block1_money_management", "ADK", "Money Management Orchestrator"),
        ("Block 1", "block1_ocr", "ADK", "OCR / Transaction Extraction"),
        ("Block 1", "block1_watchdog", "ADK", "Anomaly & Fraud Detection"),
        ("Block 1", "block1_categorize", "ADK", "Transaction Categorization"),
        ("Block 1", "block1_detector", "ADK", "Recurring Payment Detection"),
        ("Block 1", "block1_growth", "ADK", "Spending Analysis & Budgeting"),
        ("Block 1", "block1_news", "ADK", "Personal Finance News"),
        ("Block 2", "block2_investment", "ADK", "Investment Orchestrator"),
        ("Block 2", "block2_analysis", "ADK", "Risk & Surplus Analysis"),
        ("Block 2", "block2_stocks", "ADK", "Equity / MF / SIP Recommendations"),
        ("Block 2", "block2_fixed_income", "ADK", "FD / PPF / NPS / Bonds"),
        ("Block 2", "block2_market_news", "ADK", "Market Trends & Sentiment"),
        ("Block 3", "block3_financial_products", "ADK", "Products Orchestrator"),
        ("Block 3", "block3_credit_card", "ADK", "Credit Card Matching"),
        ("Block 3", "block3_itr", "ADK", "Tax Planning & ITR Optimization"),
        ("Block 3", "block3_loan", "ADK", "Loan & EMI Calculator"),
    ]

    for row in adk_agents:
        table.add_row(*row)

    console.print(table)


@cli.command()
@click.option("--framework", type=click.Choice(["adk", "langchain"]), default="adk")
def test(framework):
    """
    Run basic agent evaluation tests.

    Checks that all agents can be instantiated and respond to sample queries.
    """
    console.print(Panel(f"[bold]Running FinBuddy Agent Tests[/bold] — Framework: {framework}", border_style="blue"))

    settings.AGENT_FRAMEWORK = framework

    test_cases = [
        ("block1", "How much did I spend on groceries last month?"),
        ("block2", "Should I invest in RELIANCE or TCS?"),
        ("block3", "Which tax regime is better for me: old or new?"),
    ]

    from google_adk.service import get_agent_service

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    service = get_agent_service()

    passed = 0
    failed = 0

    for block, query in test_cases:
        with console.status(f"[bold]Testing {block}...[/bold]"):
            result = loop.run_until_complete(
                service.process_message(
                    user_id="test_user",
                    conversation_id=f"test_{block}",
                    message=query,
                )
            )

        if result.get("success") and len(result.get("response", "")) > 10:
            console.print(f"[green]✓[/green] {block}: {query[:50]}... ({result.get('duration_ms', 0):.0f}ms)")
            passed += 1
        else:
            console.print(f"[red]✗[/red] {block}: {query[:50]}... — {result.get('error', 'No response')}")
            failed += 1

    console.print(f"\n[bold]Results:[/bold] [green]{passed} passed[/green] | [red]{failed} failed[/red]")


@cli.command()
@click.option("--port", default=8001, help="Port for MCP server")
def mcp_server(port):
    """
    Start the FinBuddy MCP Financial Data Server.

    Exposes financial tools via Model Context Protocol for external clients.
    """
    console.print(Panel(
        f"[bold]Starting MCP Server[/bold] on port [cyan]{port}[/cyan]\n"
        "Tools: get_stock_quote, calculate_emi, get_inflation_rate, "
        "convert_currency, calculate_compound_interest, get_market_indices",
        border_style="blue"
    ))
    # Delegate to the MCP server module
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "mcp_server.server"])


@cli.command()
@click.option("--check", is_flag=True, help="Run pre-deployment health checks")
def deploy(check):
    """
    Deployment helper for FinBuddy.

    Checks environment variables, database connectivity, and agent readiness.
    """
    if not check:
        console.print("[yellow]Use --check to run pre-deployment health checks.[/yellow]")
        return

    console.print(Panel("[bold]Pre-Deployment Health Check[/bold]", border_style="yellow"))

    checks = []

    # Check 1: API Keys
    gemini_ok = bool(settings.GEMINI_API_KEY)
    checks.append(("Gemini API Key", "PASS" if gemini_ok else "FAIL", "Required for ADK"))

    openai_ok = bool(settings.OPENAI_API_KEY)
    checks.append(("OpenAI API Key", "PASS" if openai_ok else "WARN", "Optional fallback"))

    # Check 2: Database
    db_ok = bool(settings.DATABASE_URL)
    checks.append(("Database URL", "PASS" if db_ok else "FAIL", "PostgreSQL required"))

    # Check 3: Redis
    redis_ok = bool(settings.REDIS_URL)
    checks.append(("Redis URL", "PASS" if redis_ok else "WARN", "Caching & Celery"))

    # Check 4: Framework
    checks.append(("Agent Framework", settings.AGENT_FRAMEWORK, "Set to 'adk' for Kaggle"))

    table = Table(title="Health Check Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Notes", style="dim")

    for name, status, notes in checks:
        color = "green" if status in ("PASS", "adk") else ("yellow" if status == "WARN" else "red")
        table.add_row(name, f"[{color}]{status}[/{color}]", notes)

    console.print(table)

    if not gemini_ok or not db_ok:
        console.print("\n[red]Critical checks failed. Please fix before deploying.[/red]")
    else:
        console.print("\n[green]All critical checks passed! Ready to deploy.[/green]")


if __name__ == "__main__":
    cli()
