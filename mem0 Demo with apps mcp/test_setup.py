#!/usr/bin/env python3
"""
Test script to verify Invoice Processing Agent setup and connections
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Try to import required modules
console = Console()


def test_imports():
    """Test if all required modules can be imported"""
    rprint("[bold blue]Testing imports...[/bold blue]")

    try:
        from camel.agents import ChatAgent
        from camel.messages import BaseMessage
        from camel.models import ModelFactory
        from camel.toolkits import MCPToolkit
        from camel.types import ModelPlatformType

        rprint("[green]✓ CAMEL-AI imports successful[/green]")
    except ImportError as e:
        rprint(f"[red]✗ CAMEL-AI import failed: {e}[/red]")
        return False

    try:
        import rich

        rprint("[green]✓ Rich console imports successful[/green]")
    except ImportError as e:
        rprint(f"[red]✗ Rich import failed: {e}[/red]")
        return False

    try:
        from create_config import create_config

        rprint("[green]✓ Configuration module imports successful[/green]")
    except ImportError as e:
        rprint(f"[red]✗ Configuration import failed: {e}[/red]")
        return False

    return True


def test_environment():
    """Test environment variables"""
    rprint("\n[bold blue]Testing environment variables...[/bold blue]")

    load_dotenv()

    required_vars = ["ACI_API_KEY", "GOOGLE_API_KEY", "LINKED_ACCOUNT_OWNER_ID"]

    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            rprint(f"[red]✗ {var} not found[/red]")
        else:
            # Mask sensitive values
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            rprint(f"[green]✓ {var} found: {masked_value}[/green]")

    if missing_vars:
        rprint(
            f"\n[red]Missing required environment variables: {', '.join(missing_vars)}[/red]"
        )
        return False

    return True


async def test_mcp_connection():
    """Test MCP toolkit connection"""
    rprint("\n[bold blue]Testing MCP connection...[/bold blue]")

    try:
        from camel.toolkits import MCPToolkit
        from create_config import create_config

        # Create config
        create_config()
        rprint("[green]✓ Configuration created[/green]")

        # Test connection
        mcp_toolkit = MCPToolkit(config_path="config.json")
        await mcp_toolkit.connect()
        rprint("[green]✓ MCP toolkit connected[/green]")

        # Get tools
        tools = mcp_toolkit.get_tools()
        rprint(f"[green]✓ Found {len(tools)} available tools[/green]")

        # Display tools
        if tools:
            tool_table = Table(title="Available ACI Tools")
            tool_table.add_column("Tool Name", style="cyan")
            tool_table.add_column("Description", style="white")

            for tool in tools[:10]:  # Show first 10 tools
                name = getattr(tool, "name", "Unknown")
                desc = (
                    getattr(tool, "description", "No description")[:50] + "..."
                    if len(getattr(tool, "description", "")) > 50
                    else getattr(tool, "description", "No description")
                )
                tool_table.add_row(name, desc)

            if len(tools) > 10:
                tool_table.add_row("...", f"... and {len(tools) - 10} more tools")

            console.print(tool_table)

        # Disconnect
        await mcp_toolkit.disconnect()
        rprint("[green]✓ MCP toolkit disconnected cleanly[/green]")

        return True

    except Exception as e:
        rprint(f"[red]✗ MCP connection failed: {e}[/red]")
        return False


async def test_model_setup():
    """Test Gemini model setup"""
    rprint("\n[bold blue]Testing Gemini model setup...[/bold blue]")

    try:
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType

        model = ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type="gemini-2.5-pro-preview-05-06",
            api_key=os.getenv("GOOGLE_API_KEY"),
            model_config_dict={"temperature": 0.3, "max_tokens": 1000},
        )

        rprint("[green]✓ Gemini model created successfully[/green]")
        return True

    except Exception as e:
        rprint(f"[red]✗ Model setup failed: {e}[/red]")
        return False


def test_file_structure():
    """Test required file structure"""
    rprint("\n[bold blue]Testing file structure...[/bold blue]")

    required_files = [
        ".env",
        "create_config.py",
        "invoice_agent.py",
        "requirements.txt",
        "README.md",
    ]

    missing_files = []

    for file in required_files:
        if os.path.exists(file):
            rprint(f"[green]✓ {file} exists[/green]")
        else:
            missing_files.append(file)
            rprint(f"[red]✗ {file} missing[/red]")

    if missing_files:
        rprint(f"\n[red]Missing required files: {', '.join(missing_files)}[/red]")
        return False

    return True


async def run_full_test():
    """Run all tests"""
    console.print(
        Panel.fit(
            "[bold blue]🧪 Invoice Processing Agent - Setup Test[/bold blue]\n"
            "[white]Verifying all components are properly configured[/white]",
            border_style="blue",
        )
    )

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Model Setup", test_model_setup),
        ("MCP Connection", test_mcp_connection),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            rprint(f"[red]Test {test_name} crashed: {e}[/red]")
            results.append((test_name, False))

    # Summary
    rprint("\n[bold blue]Test Summary:[/bold blue]")

    summary_table = Table(title="Setup Test Results")
    summary_table.add_column("Test", style="white")
    summary_table.add_column("Status", style="bold")

    passed = 0
    total = len(results)

    for test_name, result in results:
        if result:
            summary_table.add_row(test_name, "[green]✓ PASSED[/green]")
            passed += 1
        else:
            summary_table.add_row(test_name, "[red]✗ FAILED[/red]")

    console.print(summary_table)

    # Final verdict
    if passed == total:
        console.print(
            Panel(
                f"[bold green]🎉 All tests passed! ({passed}/{total})[/bold green]\n"
                "[white]Your Invoice Processing Agent is ready to use![/white]\n"
                "[dim]Run 'python invoice_agent.py' to start[/dim]",
                border_style="green",
            )
        )
        return True
    else:
        console.print(
            Panel(
                f"[bold red]❌ Some tests failed ({passed}/{total} passed)[/bold red]\n"
                "[white]Please fix the issues above before running the agent[/white]\n"
                "[dim]Check the README.md for setup instructions[/dim]",
                border_style="red",
            )
        )
        return False


async def main():
    """Main test function"""
    success = await run_full_test()

    if success:
        # Offer to run a quick demo
        rprint(
            "\n[bold cyan]Would you like to run a quick connection test?[/bold cyan]"
        )
        response = input("Type 'yes' to test agent initialization: ").strip().lower()

        if response in ["yes", "y"]:
            rprint("\n[bold blue]Testing agent initialization...[/bold blue]")
            try:
                from camel.agents import ChatAgent
                from camel.messages import BaseMessage
                from camel.models import ModelFactory
                from camel.toolkits import MCPToolkit
                from camel.types import ModelPlatformType
                from create_config import create_config

                # Quick agent test
                create_config()
                mcp_toolkit = MCPToolkit(config_path="config.json")
                await mcp_toolkit.connect()

                tools = mcp_toolkit.get_tools()

                model = ModelFactory.create(
                    model_platform=ModelPlatformType.GEMINI,
                    model_type="gemini-2.5-pro-preview-05-06",
                    api_key=os.getenv("GOOGLE_API_KEY"),
                    model_config_dict={"temperature": 0.3, "max_tokens": 1000},
                )

                system_message = BaseMessage.make_assistant_message(
                    role_name="TestAgent",
                    content="You are a test agent verifying the setup.",
                )

                agent = ChatAgent(
                    system_message=system_message, model=model, tools=tools, memory=None
                )

                await mcp_toolkit.disconnect()

                rprint(
                    "[bold green]🎉 Agent initialization test successful![/bold green]"
                )
                rprint(
                    "[white]Your system is fully ready for invoice processing![/white]"
                )

            except Exception as e:
                rprint(f"[red]Agent initialization failed: {e}[/red]")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
