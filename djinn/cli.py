"""
Djinn CLI - Main command-line interface with high-impact features.

Features:
    - Auto-Execute Mode (-x): Run command directly
    - Command Confirmation: Ask before running dangerous commands
    - Alias System: Save shortcuts (@cleanup, @deploy, etc.)
    - Shell Detection: Auto-detect PowerShell/Bash/Zsh
    - Explain Mode: Explain any command
"""
import os
import sys
import json
import subprocess
import click
import pyperclip
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from djinn import __version__
from djinn.core import DjinnEngine, HistoryManager, ContextAnalyzer, AliasManager
from djinn.ui import Logo, Theme, DjinnSpinner


# Initialize console with theme
console = Console(theme=Theme.get_theme())
spinner = DjinnSpinner(console)


def get_config_path() -> Path:
    """Get the config file path."""
    config_dir = Path.home() / ".djinn"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def load_config() -> dict:
    """Load configuration from file."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path) as f:
                return json.load(f)
        except:
            pass
    return {
        "backend": "ollama",
        "model": None,
        "context_enabled": True,
        "auto_copy": True,
        "confirm_execute": True,
    }


def save_config(config: dict):
    """Save configuration to file."""
    with open(get_config_path(), "w") as f:
        json.dump(config, f, indent=2)


def execute_command(command: str, confirm: bool = True) -> bool:
    """Execute a shell command."""
    if confirm:
        console.print(f"\n[warning]About to execute:[/warning]")
        console.print(f"  [bold]{command}[/bold]\n")
        if not Confirm.ask("[prompt]Run this command?[/prompt]", default=False):
            console.print("[muted]Cancelled.[/muted]")
            return False
    
    try:
        console.print("[muted]Executing...[/muted]\n")
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")
        return False


@click.group(invoke_without_command=True)
@click.argument("prompt", nargs=-1, required=False)
@click.option("-i", "--interactive", is_flag=True, help="Interactive mode")
@click.option("-x", "--execute", is_flag=True, help="Execute the command directly")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation (use with -x)")
@click.option("-b", "--backend", type=click.Choice(["ollama", "lmstudio", "openai"]), help="LLM backend")
@click.option("-m", "--model", help="Model name")
@click.option("-c", "--context/--no-context", default=True, help="Use directory context")
@click.option("-e", "--explain", is_flag=True, help="Explain the command")
@click.option("--mini", is_flag=True, help="Use mini logo")
@click.option("-v", "--version", is_flag=True, help="Show version")
@click.pass_context
def main(ctx, prompt, interactive, execute, yes, backend, model, context, explain, mini, version):
    """
    DJINN - Terminal Sorcery at Your Command
    
    Convert natural language to shell commands using AI.
    
    Examples:
        djinn "list all files larger than 100MB"
        djinn -x "delete temp files"          # Execute directly
        djinn -x -y "create backup folder"    # Execute without confirmation
        djinn @cleanup                        # Use saved alias
    
    Commands:
        djinn alias add/remove/list           # Manage aliases
        djinn explain "command"               # Explain a command
        djinn history                         # View history
        djinn config --show                   # View config
    """
    if version:
        console.print(f"[highlight]DJINN[/highlight] version [success]{__version__}[/success]")
        return
    
    # If a subcommand was invoked, let it handle things
    if ctx.invoked_subcommand is not None:
        return
    
    # Load config
    config = load_config()
    backend = backend or config.get("backend", "ollama")
    model = model or config.get("model")
    
    # Show logo
    Logo.print_logo(console, mini=mini)
    
    if interactive:
        run_interactive(backend, model, context)
    elif prompt:
        prompt_text = " ".join(prompt)
        
        # Resolve aliases
        alias_mgr = AliasManager()
        prompt_text = alias_mgr.resolve(prompt_text)
        
        run_single(prompt_text, backend, model, context, explain, execute, not yes)
    else:
        # Show help
        console.print("\n[muted]Usage: djinn \"your command description\"[/muted]")
        console.print("[muted]       djinn -x \"command\" (execute directly)[/muted]")
        console.print("[muted]       djinn -i  (interactive mode)[/muted]")
        console.print("[muted]       djinn --help  (all options)[/muted]\n")


def run_single(prompt: str, backend: str, model: str, use_context: bool, explain: bool, execute: bool, confirm: bool):
    """Run a single command generation."""
    # Get context if enabled
    context_str = None
    analyzer = ContextAnalyzer()
    
    if use_context:
        context_str = analyzer.get_context_string()
        # Add shell info to context
        shell_info = analyzer.get_shell_info()
        context_str = f"{shell_info}\n{context_str}"
    
    # Show intent
    console.print(f"\n[prompt]> Intent:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    # Generate command
    engine = DjinnEngine(backend=backend, model=model)
    history = HistoryManager()
    
    with spinner.status("Summoning command..."):
        if explain:
            result = engine.generate_with_explanation(prompt, context_str)
            command = result["command"]
            explanation = result["explanation"]
        else:
            command = engine.generate(prompt, context_str)
            explanation = None
    
    if command:
        # Success
        spinner.print_success(command)
        
        if explanation:
            console.print(f"[muted]Explanation: {explanation}[/muted]\n")
        
        # Copy to clipboard
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
        
        # Save to history
        history.add(
            prompt=prompt,
            command=command,
            backend=backend,
            model=model,
            context=context_str
        )
        
        # Execute if requested
        if execute:
            console.print()
            execute_command(command, confirm=confirm)
    else:
        spinner.print_error("Failed to generate command. Is your LLM backend running?")


def run_interactive(backend: str, model: str, use_context: bool):
    """Run interactive mode."""
    engine = DjinnEngine(backend=backend, model=model)
    history = HistoryManager()
    analyzer = ContextAnalyzer()
    alias_mgr = AliasManager()
    
    console.print(f"\n[success]Interactive Mode[/success]")
    console.print("[muted]Commands: exit, refine <feedback>, run (execute last), aliases[/muted]\n")
    
    last_prompt = None
    last_command = None
    
    while True:
        try:
            user_input = Prompt.ask("[prompt]djinn >[/prompt]")
            
            if not user_input.strip():
                continue
            
            # Exit commands
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[muted]Goodbye![/muted]")
                break
            
            # Run last command
            if user_input.lower() == "run" and last_command:
                execute_command(last_command, confirm=True)
                continue
            
            # Show aliases
            if user_input.lower() == "aliases":
                aliases = alias_mgr.list_all()
                if aliases:
                    for name, prompt in aliases.items():
                        console.print(f"  [highlight]@{name}[/highlight]: {prompt}")
                else:
                    console.print("[muted]No aliases saved.[/muted]")
                continue
            
            # Resolve aliases
            user_input = alias_mgr.resolve(user_input)
            
            # Refine last command
            if user_input.lower().startswith("refine ") and last_command:
                feedback = user_input[7:]
                with spinner.status("Refining..."):
                    command = engine.refine(last_prompt, last_command, feedback)
            else:
                # New command
                context_str = None
                if use_context:
                    context_str = analyzer.get_context_string()
                    shell_info = analyzer.get_shell_info()
                    context_str = f"{shell_info}\n{context_str}"
                
                with spinner.status("Summoning command..."):
                    command = engine.generate(user_input, context_str)
                
                last_prompt = user_input
            
            if command:
                last_command = command
                spinner.print_success(command)
                
                try:
                    pyperclip.copy(command)
                    spinner.print_copied()
                except:
                    pass
                
                history.add(
                    prompt=user_input,
                    command=command,
                    backend=backend,
                    model=model
                )
                
                console.print()
            else:
                spinner.print_error("Failed to generate")
                console.print()
                
        except KeyboardInterrupt:
            console.print("\n[muted]Goodbye![/muted]")
            break
        except EOFError:
            break


@main.command()
@click.argument("command_text", nargs=-1, required=True)
def explain(command_text):
    """Explain what a command does."""
    command = " ".join(command_text)
    
    console.print(f"\n[prompt]> Explaining:[/prompt] {command}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    
    explain_prompt = f"Explain this command in simple terms, what it does step by step: {command}"
    
    with spinner.status("Analyzing command..."):
        explanation = engine.backend.generate(
            explain_prompt,
            "You are a helpful terminal expert. Explain commands clearly and concisely. Use bullet points."
        )
    
    if explanation:
        console.print(f"\n[success]Explanation:[/success]\n")
        console.print(explanation)
        console.print()
    else:
        spinner.print_error("Could not explain command")


@main.command()
@click.option("-l", "--limit", default=20, help="Number of entries to show")
@click.option("-s", "--search", help="Search history")
@click.option("-f", "--favorites", is_flag=True, help="Show only favorites")
def history(limit, search, favorites):
    """View command history."""
    history_mgr = HistoryManager()
    
    if favorites:
        entries = history_mgr.get_favorites()
        title = "Favorite Commands"
    elif search:
        entries = history_mgr.search(search, limit)
        title = f"Search: {search}"
    else:
        entries = history_mgr.get_recent(limit)
        title = "Recent Commands"
    
    if not entries:
        console.print("[muted]No history found.[/muted]")
        return
    
    table = Table(title=title, border_style="#22C55E")
    table.add_column("ID", style="muted", width=5)
    table.add_column("Prompt", style="prompt", max_width=30)
    table.add_column("Command", style="command", max_width=40)
    table.add_column("Fav", width=3)
    
    for entry in entries:
        fav = "*" if entry.get("favorite") else ""
        table.add_row(
            str(entry["id"]),
            entry["prompt"][:28] + "..." if len(entry["prompt"]) > 28 else entry["prompt"],
            entry["command"][:38] + "..." if len(entry["command"]) > 38 else entry["command"],
            fav
        )
    
    console.print(table)
    
    stats = history_mgr.get_stats()
    console.print(f"\n[muted]Total: {stats['total']} | Favorites: {stats['favorites']}[/muted]")


@main.command()
@click.option("--backend", type=click.Choice(["ollama", "lmstudio", "openai"]), help="Set default backend")
@click.option("--model", help="Set default model")
@click.option("--show", is_flag=True, help="Show current config")
def config(backend, model, show):
    """Configure Djinn settings."""
    current_config = load_config()
    
    if show:
        console.print("\n[highlight]Current Configuration[/highlight]\n")
        for key, value in current_config.items():
            console.print(f"  [prompt]{key}:[/prompt] {value}")
        console.print()
        return
    
    if backend:
        current_config["backend"] = backend
    if model:
        current_config["model"] = model
    
    save_config(current_config)
    console.print("[success]Configuration updated![/success]")


@main.command()
@click.argument("action", type=click.Choice(["add", "remove", "list"]))
@click.argument("name", required=False)
@click.argument("prompt_text", nargs=-1, required=False)
def alias(action, name, prompt_text):
    """Manage command aliases.
    
    Examples:
        djinn alias add cleanup "delete all temp files and cache"
        djinn alias add deploy "build and deploy to production"
        djinn alias remove cleanup
        djinn alias list
    """
    alias_mgr = AliasManager()
    
    if action == "list":
        aliases = alias_mgr.list_all()
        if aliases:
            console.print("\n[highlight]Saved Aliases[/highlight]\n")
            for alias_name, prompt in aliases.items():
                console.print(f"  [success]@{alias_name}[/success]: {prompt}")
            console.print()
        else:
            console.print("[muted]No aliases saved. Add one with: djinn alias add <name> \"<prompt>\"[/muted]")
    
    elif action == "add":
        if not name or not prompt_text:
            console.print("[error]Usage: djinn alias add <name> \"<prompt>\"[/error]")
            return
        prompt = " ".join(prompt_text)
        alias_mgr.add(name, prompt)
        console.print(f"[success]Added alias @{name}[/success]")
    
    elif action == "remove":
        if not name:
            console.print("[error]Usage: djinn alias remove <name>[/error]")
            return
        if alias_mgr.remove(name):
            console.print(f"[success]Removed alias @{name}[/success]")
        else:
            console.print(f"[error]Alias @{name} not found[/error]")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def git(prompt_text):
    """Git-specific command generator.
    
    Examples:
        djinn git "undo last commit"
        djinn git "show all branches"
        djinn git "merge feature into main"
    """
    from djinn.core.plugins import GitPlugin
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = GitPlugin(engine)
    
    console.print(f"\n[prompt]> Git:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating git command..."):
        command = plugin.generate(prompt)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate git command")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def docker(prompt_text):
    """Docker-specific command generator.
    
    Examples:
        djinn docker "cleanup unused containers"
        djinn docker "list running containers"
        djinn docker "show logs for nginx"
    """
    from djinn.core.plugins import DockerPlugin
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = DockerPlugin(engine)
    
    console.print(f"\n[prompt]> Docker:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating docker command..."):
        command = plugin.generate(prompt)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate docker command")


@main.command()
@click.argument("command_text", nargs=-1, required=True)
def undo(command_text):
    """Generate the command to undo/reverse an action.
    
    Examples:
        djinn undo "mkdir new_folder"
        djinn undo "git commit -m message"
        djinn undo "mv file.txt backup/"
    """
    from djinn.core.plugins import UndoPlugin
    
    command = " ".join(command_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = UndoPlugin(engine)
    
    console.print(f"\n[prompt]> Undo:[/prompt] {command}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating undo command..."):
        undo_cmd = plugin.generate_undo(command)
    
    if undo_cmd:
        if "IRREVERSIBLE" in undo_cmd.upper():
            console.print("[warning]This action cannot be undone![/warning]")
        else:
            spinner.print_success(undo_cmd)
            try:
                pyperclip.copy(undo_cmd)
                spinner.print_copied()
            except:
                pass
    else:
        spinner.print_error("Failed to generate undo command")


@main.command()
@click.argument("theme_name", required=False)
def theme(theme_name):
    """Change the color theme.
    
    Available themes: default, hacker, ocean, purple, minimal
    
    Examples:
        djinn theme hacker
        djinn theme ocean
        djinn theme          # Show current theme
    """
    from djinn.ui.themes import ThemeManager
    
    config = load_config()
    
    if not theme_name:
        current = config.get("theme", "default")
        available = ThemeManager.list_themes()
        console.print(f"\n[highlight]Current theme:[/highlight] {current}")
        console.print(f"[muted]Available: {', '.join(available)}[/muted]\n")
        return
    
    if theme_name not in ThemeManager.list_themes():
        console.print(f"[error]Unknown theme: {theme_name}[/error]")
        console.print(f"[muted]Available: {', '.join(ThemeManager.list_themes())}[/muted]")
        return
    
    config["theme"] = theme_name
    save_config(config)
    console.print(f"[success]Theme changed to: {theme_name}[/success]")


@main.command()
@click.argument("action", type=click.Choice(["add", "remove", "list", "run"]))
@click.argument("name", required=False)
@click.argument("params", nargs=-1, required=False)
def template(action, name, params):
    """Manage command templates.
    
    Built-in templates: python-project, node-project, git-init, docker-compose, cleanup, backup
    
    Examples:
        djinn template list
        djinn template run python-project myapp
        djinn template add mytemplate "echo hello"
    """
    from djinn.core.advanced import TemplateManager
    
    tmpl_mgr = TemplateManager()
    
    if action == "list":
        templates = tmpl_mgr.list_all()
        console.print("\n[highlight]Available Templates[/highlight]\n")
        for tname, info in templates.items():
            console.print(f"  [success]{tname}[/success]: {info.get('description', '')}")
            if info.get('params'):
                console.print(f"    [muted]Params: {', '.join(info['params'])}[/muted]")
        console.print()
    
    elif action == "run":
        if not name:
            console.print("[error]Usage: djinn template run <name> [params...][/error]")
            return
        
        template_info = tmpl_mgr.get(name)
        if not template_info:
            console.print(f"[error]Template '{name}' not found[/error]")
            return
        
        # Parse params
        kwargs = {}
        for i, param_name in enumerate(template_info.get('params', [])):
            if i < len(params):
                kwargs[param_name] = params[i]
            else:
                kwargs[param_name] = Prompt.ask(f"[prompt]{param_name}[/prompt]")
        
        command = tmpl_mgr.render(name, **kwargs)
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    
    elif action == "add":
        if not name or not params:
            console.print("[error]Usage: djinn template add <name> \"<command>\"[/error]")
            return
        command = " ".join(params)
        tmpl_mgr.add(name, command)
        console.print(f"[success]Added template: {name}[/success]")
    
    elif action == "remove":
        if not name:
            console.print("[error]Usage: djinn template remove <name>[/error]")
            return
        if tmpl_mgr.remove(name):
            console.print(f"[success]Removed template: {name}[/success]")
        else:
            console.print(f"[error]Cannot remove built-in or unknown template[/error]")


@main.command()
@click.argument("action", type=click.Choice(["add", "remove", "list", "run"]))
@click.argument("name", required=False)
@click.argument("content", nargs=-1, required=False)
def snippet(action, name, content):
    """Manage multi-line command snippets.
    
    Examples:
        djinn snippet add deploy "npm run build && scp -r dist/ user@server:/var/www"
        djinn snippet list
        djinn snippet run deploy
    """
    from djinn.core.advanced import SnippetManager
    
    snip_mgr = SnippetManager()
    
    if action == "list":
        snippets = snip_mgr.list_all()
        if snippets:
            console.print("\n[highlight]Saved Snippets[/highlight]\n")
            for sname, scontent in snippets.items():
                console.print(f"  [success]{sname}[/success]:")
                console.print(f"    [muted]{scontent[:50]}{'...' if len(scontent) > 50 else ''}[/muted]")
            console.print()
        else:
            console.print("[muted]No snippets saved.[/muted]")
    
    elif action == "run":
        if not name:
            console.print("[error]Usage: djinn snippet run <name>[/error]")
            return
        snip = snip_mgr.get(name)
        if snip:
            spinner.print_success(snip)
            try:
                pyperclip.copy(snip)
                spinner.print_copied()
            except:
                pass
        else:
            console.print(f"[error]Snippet '{name}' not found[/error]")
    
    elif action == "add":
        if not name or not content:
            console.print("[error]Usage: djinn snippet add <name> \"<content>\"[/error]")
            return
        snip_mgr.add(name, " ".join(content))
        console.print(f"[success]Added snippet: {name}[/success]")
    
    elif action == "remove":
        if snip_mgr.remove(name):
            console.print(f"[success]Removed snippet: {name}[/success]")
        else:
            console.print(f"[error]Snippet not found[/error]")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def suggest(prompt_text):
    """Generate multiple command suggestions.
    
    Shows 3 different command options to choose from.
    
    Example:
        djinn suggest "delete all log files"
    """
    from djinn.core.advanced import MultiSuggestion
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    
    console.print(f"\n[prompt]> Suggestions for:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating options..."):
        multi = MultiSuggestion(engine)
        suggestions = multi.generate(prompt)
    
    if suggestions:
        console.print("\n[highlight]Choose a command:[/highlight]\n")
        for i, cmd in enumerate(suggestions, 1):
            console.print(f"  [success]{i}.[/success] {cmd}")
        
        console.print()
        choice = Prompt.ask("[prompt]Select (1-3)[/prompt]", choices=["1", "2", "3"], default="1")
        
        chosen = suggestions[int(choice) - 1]
        spinner.print_success(chosen)
        try:
            pyperclip.copy(chosen)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate suggestions")


@main.command()
@click.argument("server")
@click.argument("prompt_text", nargs=-1, required=True)
def ssh(server, prompt_text):
    """Generate SSH commands for remote servers.
    
    Examples:
        djinn ssh user@host "check disk space"
        djinn ssh myserver "view nginx logs"
    """
    from djinn.core.network import SSHPlugin
    
    prompt = " ".join(prompt_text)
    
    # Parse user@host
    if "@" in server:
        user, host = server.split("@", 1)
    else:
        user, host = "root", server
    
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = SSHPlugin(engine)
    
    console.print(f"\n[prompt]> SSH ({user}@{host}):[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating SSH command..."):
        command = plugin.generate(prompt, user, host)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate SSH command")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def api(prompt_text):
    """Generate API/curl commands.
    
    Examples:
        djinn api "get weather for London"
        djinn api "post json to https://api.example.com"
    """
    from djinn.core.network import APIPlugin
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = APIPlugin(engine)
    
    console.print(f"\n[prompt]> API:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating curl command..."):
        command = plugin.generate(prompt)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate API command")


@main.command()
@click.argument("command_text", nargs=-1, required=True)
def check(command_text):
    """Check if a command is dangerous.
    
    Example:
        djinn check "rm -rf /"
    """
    from djinn.core.advanced import DangerDetector
    
    command = " ".join(command_text)
    warnings = DangerDetector.check(command)
    
    console.print(f"\n[prompt]> Checking:[/prompt] {command}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    if warnings:
        console.print("\n[error]⚠️  DANGER DETECTED![/error]\n")
        for w in warnings:
            console.print(f"  [warning]• {w['description']}[/warning]")
        console.print()
    else:
        console.print("\n[success]✓ Command appears safe[/success]\n")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def aws(prompt_text):
    """AWS CLI command generator.
    
    Examples:
        djinn aws "list all s3 buckets"
        djinn aws "deploy lambda function"
    """
    from djinn.core.cloud import AWSPlugin
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = AWSPlugin(engine)
    
    console.print(f"\n[prompt]> AWS:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating AWS command..."):
        command = plugin.generate(prompt)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate AWS command")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def gcp(prompt_text):
    """GCP gcloud command generator.
    
    Examples:
        djinn gcp "list compute instances"
        djinn gcp "deploy cloud function"
    """
    from djinn.core.cloud import GCPPlugin
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = GCPPlugin(engine)
    
    console.print(f"\n[prompt]> GCP:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating gcloud command..."):
        command = plugin.generate(prompt)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate GCP command")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def azure(prompt_text):
    """Azure CLI command generator.
    
    Examples:
        djinn azure "list virtual machines"
        djinn azure "create storage account"
    """
    from djinn.core.cloud import AzurePlugin
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = AzurePlugin(engine)
    
    console.print(f"\n[prompt]> Azure:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating az command..."):
        command = plugin.generate(prompt)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate Azure command")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def k8s(prompt_text):
    """Kubernetes kubectl command generator.
    
    Examples:
        djinn k8s "list all pods"
        djinn k8s "scale deployment to 3 replicas"
    """
    from djinn.core.cloud import K8sPlugin
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = K8sPlugin(engine)
    
    console.print(f"\n[prompt]> Kubernetes:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating kubectl command..."):
        command = plugin.generate(prompt)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate kubectl command")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def terraform(prompt_text):
    """Terraform command generator.
    
    Examples:
        djinn terraform "initialize project"
        djinn terraform "apply changes"
    """
    from djinn.core.cloud import TerraformPlugin
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = TerraformPlugin(engine)
    
    console.print(f"\n[prompt]> Terraform:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating terraform command..."):
        command = plugin.generate(prompt)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate terraform command")


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def helm(prompt_text):
    """Helm chart command generator.
    
    Examples:
        djinn helm "install nginx"
        djinn helm "list releases"
    """
    from djinn.core.cloud import HelmPlugin
    
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    plugin = HelmPlugin(engine)
    
    console.print(f"\n[prompt]> Helm:[/prompt] {prompt}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Generating helm command..."):
        command = plugin.generate(prompt)
    
    if command:
        spinner.print_success(command)
        try:
            pyperclip.copy(command)
            spinner.print_copied()
        except:
            pass
    else:
        spinner.print_error("Failed to generate helm command")


@main.command()
@click.argument("command_text", nargs=-1, required=True)
def dryrun(command_text):
    """Dry-run: Explain what a command would do without running it.
    
    Examples:
        djinn dryrun "rm -rf /tmp/*"
        djinn dryrun "docker system prune -a"
    """
    from djinn.core.interactive import DryRun
    
    command = " ".join(command_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    analyzer = DryRun(engine)
    
    console.print(f"\n[prompt]> Dry-Run:[/prompt] {command}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    with spinner.status("Analyzing command..."):
        analysis = analyzer.analyze(command)
    
    if analysis:
        console.print("\n[highlight]What this command would do:[/highlight]\n")
        console.print(analysis)
        console.print()
    else:
        spinner.print_error("Failed to analyze command")


@main.command()
@click.argument("query", required=False)
def fuzzy(query):
    """Fuzzy search through command history.
    
    Examples:
        djinn fuzzy "docker"
        djinn fuzzy "delete"
    """
    from djinn.core.interactive import FuzzySearch
    
    if not query:
        query = Prompt.ask("[prompt]Search[/prompt]")
    
    fuzzy_search = FuzzySearch(HistoryManager())
    results = fuzzy_search.search(query)
    
    if results:
        console.print(f"\n[highlight]Results for '{query}':[/highlight]\n")
        for i, r in enumerate(results, 1):
            score = int(r['score'] * 100)
            console.print(f"  [success]{i}.[/success] [{score}%] {r['prompt']}")
            console.print(f"     [muted]{r['command']}[/muted]")
        console.print()
    else:
        console.print(f"[muted]No matches for '{query}'[/muted]")


# === SYSADMIN COMMANDS ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def npm(prompt_text):
    """NPM/Node.js command generator."""
    from djinn.core.sysadmin import NpmPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating npm command..."):
        command = NpmPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def pip(prompt_text):
    """Python pip command generator."""
    from djinn.core.sysadmin import PipPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating pip command..."):
        command = PipPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def systemctl(prompt_text):
    """Systemctl/service management."""
    from djinn.core.sysadmin import SystemctlPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating systemctl command..."):
        command = SystemctlPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def cron(prompt_text):
    """Cron job generator."""
    from djinn.core.sysadmin import CronPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating cron expression..."):
        command = CronPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def nginx(prompt_text):
    """Nginx command/config generator."""
    from djinn.core.sysadmin import NginxPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating nginx command..."):
        command = NginxPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def mysql(prompt_text):
    """MySQL command/query generator."""
    from djinn.core.sysadmin import MySQLPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating MySQL command..."):
        command = MySQLPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def postgres(prompt_text):
    """PostgreSQL command generator."""
    from djinn.core.sysadmin import PostgresPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating PostgreSQL command..."):
        command = PostgresPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def redis(prompt_text):
    """Redis command generator."""
    from djinn.core.sysadmin import RedisPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Redis command..."):
        command = RedisPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def mongo(prompt_text):
    """MongoDB command generator."""
    from djinn.core.sysadmin import MongoPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating MongoDB command..."):
        command = MongoPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def ffmpeg(prompt_text):
    """FFmpeg multimedia command generator."""
    from djinn.core.sysadmin import FFmpegPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating FFmpeg command..."):
        command = FFmpegPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def magick(prompt_text):
    """ImageMagick command generator."""
    from djinn.core.sysadmin import ImageMagickPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating ImageMagick command..."):
        command = ImageMagickPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


# === SECURITY COMMANDS ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def firewall(prompt_text):
    """Firewall (ufw/iptables) command generator."""
    from djinn.core.security import FirewallPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating firewall command..."):
        command = FirewallPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def ssl(prompt_text):
    """SSL/TLS certificate command generator."""
    from djinn.core.security import SSLPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating SSL command..."):
        command = SSLPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def network(prompt_text):
    """Network diagnostics command generator."""
    from djinn.core.security import NetworkPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating network command..."):
        command = NetworkPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def process(prompt_text):
    """Process management command generator."""
    from djinn.core.security import ProcessPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating process command..."):
        command = ProcessPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def disk(prompt_text):
    """Disk management command generator."""
    from djinn.core.security import DiskPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating disk command..."):
        command = DiskPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def user(prompt_text):
    """User management command generator."""
    from djinn.core.security import UserPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating user command..."):
        command = UserPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


# === DEVELOPER TOOLS ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def pytest(prompt_text):
    """Pytest command generator."""
    from djinn.core.devtools import PytestPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating pytest command..."):
        command = PytestPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def lint(prompt_text):
    """Linting command generator (flake8, eslint, black, prettier)."""
    from djinn.core.devtools import LintPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating lint command..."):
        command = LintPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def debug(prompt_text):
    """Debugging command generator (pdb, gdb, strace)."""
    from djinn.core.devtools import DebugPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating debug command..."):
        command = DebugPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def bench(prompt_text):
    """Benchmarking command generator."""
    from djinn.core.devtools import BenchmarkPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating benchmark command..."):
        command = BenchmarkPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def regex(prompt_text):
    """Regex pattern generator."""
    from djinn.core.devtools import RegexPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating regex pattern..."):
        pattern = RegexPlugin(engine).generate(prompt)
    if pattern:
        spinner.print_success(pattern)
        try: pyperclip.copy(pattern)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def awk(prompt_text):
    """AWK/sed command generator."""
    from djinn.core.devtools import AwkSedPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating awk/sed command..."):
        command = AwkSedPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def jq(prompt_text):
    """jq JSON processing command generator."""
    from djinn.core.devtools import JqPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating jq command..."):
        command = JqPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def make(prompt_text):
    """Make/Makefile command generator."""
    from djinn.core.devtools import MakePlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating make command..."):
        command = MakePlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


# === WEB UTILITIES ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def scrape(prompt_text):
    """Web scraping command generator."""
    from djinn.core.webutils import ScrapingPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating scrape command..."):
        command = ScrapingPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def base64cmd(prompt_text):
    """Base64 encoding/decoding command generator."""
    from djinn.core.webutils import Base64Plugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating base64 command..."):
        command = Base64Plugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def hash(prompt_text):
    """Hashing command generator (md5, sha256)."""
    from djinn.core.webutils import HashPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating hash command..."):
        command = HashPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def date(prompt_text):
    """Date/time command generator."""
    from djinn.core.webutils import DateTimePlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating date command..."):
        command = DateTimePlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def archive(prompt_text):
    """Archive/compression command generator (tar, zip, gzip)."""
    from djinn.core.webutils import ArchivePlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating archive command..."):
        command = ArchivePlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def rsync(prompt_text):
    """Rsync sync command generator."""
    from djinn.core.webutils import RsyncPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating rsync command..."):
        command = RsyncPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def find(prompt_text):
    """Find command generator."""
    from djinn.core.webutils import FindPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating find command..."):
        command = FindPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def xargs(prompt_text):
    """xargs command generator."""
    from djinn.core.webutils import XargsPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating xargs command..."):
        command = XargsPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


# === LANGUAGE PLUGINS ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def python(prompt_text):
    """Python development command generator."""
    from djinn.core.languages import PythonPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Python command..."):
        command = PythonPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def node(prompt_text):
    """Node.js development command generator."""
    from djinn.core.languages import NodePlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Node.js command..."):
        command = NodePlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def rust(prompt_text):
    """Rust/Cargo command generator."""
    from djinn.core.languages import RustPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Rust command..."):
        command = RustPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def go(prompt_text):
    """Go development command generator."""
    from djinn.core.languages import GoPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Go command..."):
        command = GoPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def java(prompt_text):
    """Java/Maven/Gradle command generator."""
    from djinn.core.languages import JavaPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Java command..."):
        command = JavaPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def cpp(prompt_text):
    """C++ compilation command generator."""
    from djinn.core.languages import CppPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating C++ command..."):
        command = CppPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


# === AI UTILITIES ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def oneliner(prompt_text):
    """Generate powerful one-liner commands."""
    from djinn.core.ai import OneLinersPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating one-liner..."):
        command = OneLinersPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def script(prompt_text):
    """Generate complete shell scripts."""
    from djinn.core.ai import ScriptPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating shell script..."):
        script_code = ScriptPlugin(engine).generate(prompt)
    if script_code:
        console.print("\n[highlight]Generated Script:[/highlight]\n")
        console.print(script_code)
        try: pyperclip.copy(script_code)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("code", nargs=-1, required=True)
@click.option("--from", "from_shell", default="bash", help="Source shell")
@click.option("--to", "to_shell", default="powershell", help="Target shell")
def translate(code, from_shell, to_shell):
    """Translate commands between shells (bash, powershell, zsh)."""
    from djinn.core.ai import TranslatePlugin
    command = " ".join(code)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    
    console.print(f"\n[prompt]> Translate {from_shell} → {to_shell}:[/prompt] {command}")
    
    with spinner.status("Translating command..."):
        translated = TranslatePlugin(engine).translate(command, from_shell, to_shell)
    if translated:
        spinner.print_success(translated)
        try: pyperclip.copy(translated)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
@click.option("--lang", default="python", help="Programming language")
def codegen(prompt_text, lang):
    """Generate code snippets in any language."""
    from djinn.core.ai import CodeGenPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    
    with spinner.status(f"Generating {lang} code..."):
        code = CodeGenPlugin(engine).generate(prompt, lang)
    if code:
        console.print(f"\n[highlight]{lang.capitalize()} Code:[/highlight]\n")
        console.print(code)
        try: pyperclip.copy(code)
        except: pass
        spinner.print_copied()


@main.command()
def chat():
    """Start AI conversation mode."""
    from djinn.core.ai import ConversationPlugin
    
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    conv = ConversationPlugin(engine)
    
    console.print("\n[highlight]Chat Mode[/highlight] - type 'exit' to quit\n")
    
    while True:
        try:
            user_input = Prompt.ask("[prompt]you >[/prompt]")
            if user_input.lower() in ["exit", "quit", "q"]:
                break
            
            with spinner.status("Thinking..."):
                response = conv.chat(user_input)
            
            if response:
                console.print(f"[success]djinn >[/success] {response}\n")
        except KeyboardInterrupt:
            break
    
    console.print("[muted]Goodbye![/muted]")


# === SPECIALIZED TOOLS ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def latex(prompt_text):
    """LaTeX document command generator."""
    from djinn.core.specialized import LatexPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating LaTeX..."):
        command = LatexPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def sql(prompt_text):
    """SQL query generator."""
    from djinn.core.specialized import SQLPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating SQL..."):
        command = SQLPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def graphql(prompt_text):
    """GraphQL query generator."""
    from djinn.core.specialized import GraphQLPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating GraphQL..."):
        command = GraphQLPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def ansible(prompt_text):
    """Ansible playbook command generator."""
    from djinn.core.specialized import AnsiblePlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Ansible..."):
        command = AnsiblePlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def vagrant(prompt_text):
    """Vagrant VM command generator."""
    from djinn.core.specialized import VagrantPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Vagrant..."):
        command = VagrantPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def grpc(prompt_text):
    """gRPC/grpcurl command generator."""
    from djinn.core.specialized import GrpcPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating gRPC..."):
        command = GrpcPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


# === MOBILE & FRONTEND ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def react(prompt_text):
    """React/Next.js command generator."""
    from djinn.core.mobile import ReactPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating React..."):
        command = ReactPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def flutter(prompt_text):
    """Flutter/Dart command generator."""
    from djinn.core.mobile import FlutterPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Flutter..."):
        command = FlutterPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def android(prompt_text):
    """Android/ADB command generator."""
    from djinn.core.mobile import AndroidPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating ADB..."):
        command = AndroidPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def ios(prompt_text):
    """iOS/Xcode command generator."""
    from djinn.core.mobile import IOSPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating iOS..."):
        command = IOSPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


# === DATA & ML ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def pandas(prompt_text):
    """Pandas data manipulation code generator."""
    from djinn.core.dataml import PandasPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Pandas code..."):
        command = PandasPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def spark(prompt_text):
    """Apache Spark command generator."""
    from djinn.core.dataml import SparkPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Spark..."):
        command = SparkPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def jupyter(prompt_text):
    """Jupyter notebook command generator."""
    from djinn.core.dataml import JupyterPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating Jupyter..."):
        command = JupyterPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


# === PRODUCTIVITY ===

@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def todo(prompt_text):
    """Generate TODO comments."""
    from djinn.core.productivity import TodoPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating TODO..."):
        command = TodoPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def changelog(prompt_text):
    """Generate changelog entries."""
    from djinn.core.productivity import ChangelogPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating changelog..."):
        entry = ChangelogPlugin(engine).generate(prompt)
    if entry:
        console.print("\n[highlight]Changelog Entry:[/highlight]\n")
        console.print(entry)
        try: pyperclip.copy(entry)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def readme(prompt_text):
    """Generate README sections."""
    from djinn.core.productivity import ReadmePlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating README..."):
        section = ReadmePlugin(engine).generate(prompt)
    if section:
        console.print("\n[highlight]README Section:[/highlight]\n")
        console.print(section)
        try: pyperclip.copy(section)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def docs(prompt_text):
    """Generate documentation."""
    from djinn.core.productivity import DocsPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating docs..."):
        doc = DocsPlugin(engine).generate(prompt)
    if doc:
        console.print("\n[highlight]Documentation:[/highlight]\n")
        console.print(doc)
        try: pyperclip.copy(doc)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def commit(prompt_text):
    """Generate conventional commit messages."""
    from djinn.core.productivity import CommitPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating commit message..."):
        msg = CommitPlugin(engine).generate(prompt)
    if msg:
        spinner.print_success(msg)
        try: pyperclip.copy(msg)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def nmap(prompt_text):
    """Nmap network scanning command generator."""
    from djinn.core.productivity import NmapPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating nmap..."):
        command = NmapPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
@click.argument("prompt_text", nargs=-1, required=True)
def gpg(prompt_text):
    """GPG encryption command generator."""
    from djinn.core.productivity import GpgPlugin
    prompt = " ".join(prompt_text)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"))
    with spinner.status("Generating GPG..."):
        command = GpgPlugin(engine).generate(prompt)
    if command:
        spinner.print_success(command)
        try: pyperclip.copy(command)
        except: pass
        spinner.print_copied()


@main.command()
def credits():
    """Show credits and info."""
    Logo.print_logo(console)
    Logo.print_credits(console)
    console.print(f"\n[muted]Version: {__version__}[/muted]")


if __name__ == "__main__":
    main()
