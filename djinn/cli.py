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
from djinn.core.autofix import AutoFixPlugin
from djinn.ui import Logo, Theme, DjinnSpinner


import ctypes
# Initialize console with theme
console = Console(theme=Theme.get_theme())
spinner = DjinnSpinner(console)

def set_console_title():
    """Set the terminal window title on Windows."""
    if sys.platform == "win32":
        try:
            ctypes.windll.kernel32.SetConsoleTitleW("DJINN - Terminal Sorcery")
        except:
            pass


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
    return {}


def save_config(config: dict):
    """Save configuration to file."""
    with open(get_config_path(), "w") as f:
        json.dump(config, f, indent=2)


def execute_command(command: str, confirm: bool = True) -> tuple:
    """Execute a shell command. Returns (success, error_output)."""
    if confirm:
        console.print(f"\n[warning]About to execute:[/warning]")
        console.print(f"  [bold]{command}[/bold]\n")
        if not Confirm.ask("[prompt]Run this command?[/prompt]", default=False):
            console.print("[muted]Cancelled.[/muted]")
            return False, ""
    
    try:
        console.print("[muted]Executing...[/muted]\n")
        # Use Popen to stream stdout to console while capturing stderr
        # Actually simpler: inherit stdout (goes to console), capture stderr
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            stdout=None, # Inherit -> prints to console directly
            stderr=subprocess.PIPE # Capture for auto-fix
        )
        
        if result.returncode != 0:
            console.print(f"[error]{result.stderr}[/error]")
            return False, result.stderr
            
        return True, ""
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")
        return False, str(e)


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
    
    # If no config (first time), run setup
    if not config and not version:
        ctx.invoke(setup)
        config = load_config()
        if not config: # If user cancelled setup
            return

    backend = backend or config.get("backend", "ollama")
    model = model or config.get("model")
    api_key = config.get("api_key")
    
    # Show logo
    set_console_title()
    Logo.print_logo(console, mini=mini)
    
    if interactive:
        run_interactive(backend, model, context, api_key)
    elif prompt:
        prompt_text = " ".join(prompt)
        
        # Resolve aliases
        alias_mgr = AliasManager()
        prompt_text = alias_mgr.resolve(prompt_text)
        
        run_single(prompt_text, backend, model, context, explain, execute, not yes, api_key)
    else:
        # If running as a frozen executable (EXE) and no args, enter interactive mode automatically
        if getattr(sys, 'frozen', False):
            run_interactive(backend, model, context)
        else:
            # Show help
            console.print("\n[muted]Usage: djinn \"your command description\"[/muted]")
            console.print("[muted]       djinn -x \"command\" (execute directly)[/muted]")
            console.print("[muted]       djinn -i  (interactive mode)[/muted]")
            console.print("[muted]       djinn --help  (all options)[/muted]\n")


def run_single(prompt: str, backend: str, model: str, use_context: bool, explain: bool, execute: bool, confirm: bool, api_key: str = None):
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
    engine = DjinnEngine(backend=backend, model=model, api_key=api_key)
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
            success, error = execute_command(command, confirm=confirm)
            
            # Auto-Fix Logic
            if not success and error:
                if Confirm.ask("\n[bold red]Command failed. Attempt auto-fix?[/bold red]", default=True):
                    fix_plugin = AutoFixPlugin(engine)
                    with spinner.status("Analyzing error and generating fix..."):
                        fixed_command = fix_plugin.generate_fix(command, error)
                    
                    if fixed_command:
                        console.print(f"\n[success]Suggested Fix:[/success] {fixed_command}\n")
                        success, _ = execute_command(fixed_command, confirm=True)
                        if success:
                            console.print("[success]Fix successful![/success]")
                    else:
                        console.print("[error]Could not generate a fix.[/error]")
    else:
        spinner.print_error("Failed to generate command. Is your LLM backend running?")


def run_interactive(backend: str, model: str, use_context: bool, api_key: str = None):
    """Run interactive mode."""
    engine = DjinnEngine(backend=backend, model=model, api_key=api_key)
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
                if getattr(sys, 'frozen', False):
                    console.print("\n[muted]Press Enter to exit...[/muted]")
                    input()
                break
            
            # Run last command
            if user_input.lower() == "run" and last_command:
                success, error = execute_command(last_command, confirm=True)
                if not success and error:
                     if Confirm.ask("\n[bold red]Command failed. Attempt auto-fix?[/bold red]", default=True):
                        fix_plugin = AutoFixPlugin(engine)
                        with spinner.status("Analyzing error..."):
                            fixed_command = fix_plugin.generate_fix(last_command, error)
                        
                        if fixed_command:
                            console.print(f"\n[success]Suggested Fix:[/success] {fixed_command}\n")
                            last_command = fixed_command # Update last command
                            execute_command(fixed_command, confirm=True)
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
    if not current_config:
        current_config = {
            "backend": "ollama",
            "model": None,
            "context_enabled": True,
            "auto_copy": True,
            "confirm_execute": True,
        }
    
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
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish", "powershell"]), required=False)
def completion(shell):
    """Generate shell completion script.
    
    Usage:
        djinn completion bash > ~/.djinn-completion.bash
        source ~/.djinn-completion.bash
    """
    if not shell:
        console.print("\n[highlight]Shell Completion Setup[/highlight]\n")
        console.print("To enable tab completion, run one of the following:\n")
        console.print("  [prompt]Bash:[/prompt]       eval \"$(_DJINN_COMPLETE=bash_source djinn)\"")
        console.print("  [prompt]Zsh:[/prompt]        eval \"$(_DJINN_COMPLETE=zsh_source djinn)\"")
        console.print("  [prompt]Fish:[/prompt]       eval \"(env _DJINN_COMPLETE=fish_source djinn)\"")
        console.print("  [prompt]PowerShell:[/prompt] $env:_DJINN_COMPLETE = \"powershell_source\"")
        console.print("                 djinn | Out-String | Invoke-Expression")
        console.print("\n[muted]Add the relevant line to your shell config file (.bashrc, .zshrc, etc.) to make it permanent.[/muted]\n")
        return

    os.environ[f"_DJINN_COMPLETE"] = f"{shell}_source"
    subprocess.run("djinn", shell=True)



@main.command()
def setup():
    """Guided setup for first-time users."""
    from djinn.backends.ollama import OllamaBackend
    from djinn.backends.lmstudio import LMStudioBackend
    
    Logo.print_logo(console)
    console.print("\n[highlight]🧞‍♂️ Welcome to the DJINN Setup Wizard![/highlight]")
    console.print("[muted]Let's get your AI backend configured so you can start using Terminal Sorcery.[/muted]\n")
    
    # 1. Detection
    with spinner.status("Detecting local LLMs..."):
        ollama = OllamaBackend()
        lmstudio = LMStudioBackend()
        
        has_ollama = ollama.is_available()
        has_lmstudio = lmstudio.is_available()
    
    options = []
    if has_ollama:
        options.append("ollama")
        console.print("[success]✔ Detected Ollama running on localhost:11434[/success]")
    if has_lmstudio:
        options.append("lmstudio")
        console.print("[success]✔ Detected LM Studio running on localhost:1234[/success]")
    
    options.append("openai")
    
    # 2. Choose Backend
    choices = ["ollama", "lmstudio", "openai"]
    default_choice = options[0] if options else "ollama"
    
    console.print("\n[prompt]Which LLM backend do you want to use?[/prompt]")
    if has_ollama or has_lmstudio:
        console.print(f"[muted]Recommended based on detection: [bold]{default_choice}[/bold][/muted]")
    
    selected_backend = Prompt.ask(
        "Backend",
        choices=choices,
        default=default_choice
    )
    
    new_config = {
        "backend": selected_backend,
        "model": None,
        "context_enabled": True,
        "auto_copy": True,
        "confirm_execute": True,
    }
    
    # 3. Model / API Key
    if selected_backend == "openai":
        api_key = Prompt.ask("[prompt]Enter your OpenAI API Key[/prompt]", password=True)
        if api_key:
            # We store it in env or config
            new_config["api_key"] = api_key
        new_config["model"] = Prompt.ask("Model name", default="gpt-4o")
    
    elif selected_backend == "ollama":
        models = ollama.list_models()
        if models:
            console.print(f"\n[muted]Detected models: {', '.join(models)}[/muted]")
            new_config["model"] = Prompt.ask("Choose model", choices=models, default=models[0])
        else:
            new_config["model"] = Prompt.ask("Model name (e.g. llama3)", default="llama3")
            
    elif selected_backend == "lmstudio":
        console.print("[muted]Note: LM Studio uses whichever model you have loaded in the app.[/muted]")
        new_config["model"] = "local-model"

    # 4. Save
    save_config(new_config)
    console.print("\n[success]✨ Setup Complete![/success]")
    console.print("[muted]You are now ready to use DJINN.[/muted]")
    console.print("\nTry running: [bold]djinn \"list all files in this directory\"[/bold]\n")
    
    if getattr(sys, 'frozen', False):
        console.print("[muted]Press Enter to continue...[/muted]")
        input()


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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
    
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
    
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
    
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
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


# ============================================================================
# NEW v1.0.2 COMMANDS
# ============================================================================

@main.command()
def stats():
    """Show usage statistics.
    
    Display personal usage statistics including:
    - Total commands generated
    - Success rate
    - Most used plugins
    - Time saved estimate
    """
    from djinn.core.stats import StatsManager
    from rich.table import Table
    from rich.panel import Panel
    
    stats_mgr = StatsManager()
    summary = stats_mgr.get_summary()
    
    console.print("\n[highlight]📊 DJINN Usage Statistics[/highlight]\n")
    
    # Main stats panel
    stats_text = f"""[success]Total Commands:[/success] {summary['total_commands']}
[success]Success Rate:[/success] {summary['success_rate']}%
[success]Today:[/success] {summary['today']} commands
[success]This Week:[/success] {summary['this_week']} commands
[success]Time Saved:[/success] ~{summary['time_saved_minutes']} minutes"""
    
    console.print(Panel(stats_text, title="Overview", border_style="green"))
    
    # Top plugins
    if summary['top_plugins']:
        table = Table(title="Top Plugins", border_style="green")
        table.add_column("Plugin", style="command")
        table.add_column("Uses", style="success")
        for plugin, count in summary['top_plugins'].items():
            table.add_row(plugin or "general", str(count))
        console.print(table)
    
    # Daily activity
    activity = stats_mgr.get_daily_activity(7)
    if activity:
        console.print("\n[muted]Daily Activity (last 7 days):[/muted]")
        for day in activity:
            bar = "█" * min(day['count'], 20)
            console.print(f"  {day['date']}: {bar} {day['count']}")
    
    console.print()


@main.command()
@click.argument("modification", nargs=-1, required=False)
def redo(modification):
    """Re-run the last command with optional modifications.
    
    Examples:
        djinn redo                    # Re-run last command as-is
        djinn redo --verbose          # Re-run with --verbose added
        djinn redo but for python3    # Modify the command with AI
    """
    history = HistoryManager()
    recent = history.get_recent(1)
    
    if not recent:
        console.print("[error]No previous command found in history.[/error]")
        return
    
    last_entry = recent[0]
    last_command = last_entry['command']
    last_prompt = last_entry['prompt']
    
    console.print(f"\n[muted]Last command:[/muted] {last_command}")
    
    if modification:
        mod_text = " ".join(modification)
        
        # If it looks like a flag, just append
        if mod_text.startswith("--") or mod_text.startswith("-"):
            new_command = f"{last_command} {mod_text}"
            console.print(f"[success]Modified:[/success] {new_command}")
        else:
            # Use AI to modify
            config = load_config()
            engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
            
            with spinner.status("Modifying command..."):
                prompt = f"Original: {last_command}\nModify it to: {mod_text}\nOutput only the modified command."
                new_command = engine.backend.generate(prompt, "You modify shell commands based on instructions. Output only the command.")
            
            if new_command:
                console.print(f"[success]Modified:[/success] {new_command}")
            else:
                console.print("[error]Could not modify command.[/error]")
                return
    else:
        new_command = last_command
    
    try:
        pyperclip.copy(new_command)
        spinner.print_copied()
    except:
        pass


@main.command()
@click.argument("action", type=click.Choice(["list", "get", "clear", "search"]), required=False, default="list")
@click.argument("query", required=False)
def clipboard(action, query):
    """View and manage clipboard history.
    
    Examples:
        djinn clipboard              # List recent
        djinn clipboard list         # List recent
        djinn clipboard get 1        # Get most recent
        djinn clipboard search git   # Search for 'git'
        djinn clipboard clear        # Clear history
    """
    from djinn.core.clipboard import ClipboardManager
    
    clip_mgr = ClipboardManager()
    
    if action == "list":
        entries = clip_mgr.get_recent(10)
        if entries:
            console.print("\n[highlight]📋 Clipboard History[/highlight]\n")
            for i, entry in enumerate(entries, 1):
                console.print(f"  [success]{i}.[/success] {entry['command'][:60]}{'...' if len(entry['command']) > 60 else ''}")
                if entry.get('prompt'):
                    console.print(f"     [muted]({entry['prompt'][:40]})[/muted]")
            console.print()
        else:
            console.print("[muted]No clipboard history.[/muted]")
    
    elif action == "get":
        if query and query.isdigit():
            entry = clip_mgr.get(int(query))
            if entry:
                console.print(f"\n[command]{entry['command']}[/command]\n")
                try:
                    pyperclip.copy(entry['command'])
                    spinner.print_copied()
                except:
                    pass
            else:
                console.print("[error]Entry not found.[/error]")
        else:
            console.print("[error]Usage: djinn clipboard get <number>[/error]")
    
    elif action == "search":
        if query:
            results = clip_mgr.search(query)
            if results:
                console.print(f"\n[highlight]Search results for '{query}':[/highlight]\n")
                for entry in results[:10]:
                    console.print(f"  [command]{entry['command'][:60]}[/command]")
            else:
                console.print("[muted]No matches found.[/muted]")
        else:
            console.print("[error]Usage: djinn clipboard search <query>[/error]")
    
    elif action == "clear":
        clip_mgr.clear()
        console.print("[success]Clipboard history cleared.[/success]")


@main.command()
@click.argument("action", type=click.Choice(["add", "get", "list", "remove"]))
@click.argument("name", required=False)
@click.argument("command_or_desc", nargs=-1, required=False)
def vault(action, name, command_or_desc):
    """Securely store sensitive command snippets.
    
    Examples:
        djinn vault add ssh-prod "ssh -i ~/.ssh/key user@prod.server.com" "Production SSH"
        djinn vault list
        djinn vault get ssh-prod
        djinn vault remove ssh-prod
    """
    from djinn.core.vault import VaultManager
    
    vault_mgr = VaultManager()
    
    if action == "list":
        entries = vault_mgr.list_all()
        if entries:
            console.print("\n[highlight]🔐 Vault Entries[/highlight]\n")
            for entry_name, desc in entries.items():
                console.print(f"  [success]{entry_name}[/success]: {desc or '[no description]'}")
            console.print("\n[muted]Use 'djinn vault get <name>' to retrieve a command.[/muted]\n")
        else:
            console.print("[muted]Vault is empty.[/muted]")
    
    elif action == "add":
        if not name or not command_or_desc:
            console.print("[error]Usage: djinn vault add <name> \"<command>\" [description][/error]")
            return
        parts = list(command_or_desc)
        command = parts[0] if parts else ""
        description = " ".join(parts[1:]) if len(parts) > 1 else ""
        vault_mgr.add(name, command, description)
        console.print(f"[success]Added '{name}' to vault.[/success]")
    
    elif action == "get":
        if not name:
            console.print("[error]Usage: djinn vault get <name>[/error]")
            return
        command = vault_mgr.get(name)
        if command:
            console.print(f"\n[command]{command}[/command]\n")
            try:
                pyperclip.copy(command)
                spinner.print_copied()
            except:
                pass
        else:
            console.print(f"[error]Entry '{name}' not found.[/error]")
    
    elif action == "remove":
        if vault_mgr.remove(name):
            console.print(f"[success]Removed '{name}' from vault.[/success]")
        else:
            console.print(f"[error]Entry '{name}' not found.[/error]")


@main.command()
@click.argument("action", type=click.Choice(["list", "available", "install", "uninstall"]))
@click.argument("plugin_name", required=False)
def plugin(action, plugin_name):
    """Manage community plugins.
    
    Examples:
        djinn plugin available       # Show available plugins
        djinn plugin list            # Show installed plugins
        djinn plugin install aws-extended
        djinn plugin uninstall aws-extended
    """
    from djinn.core.marketplace import PluginMarketplace
    
    marketplace = PluginMarketplace()
    
    if action == "available":
        plugins = marketplace.list_available()
        console.print("\n[highlight]🧩 Available Plugins[/highlight]\n")
        for p in plugins:
            console.print(f"  [success]{p['name']}[/success] v{p['version']}")
            console.print(f"    [muted]{p['description']}[/muted]")
        console.print("\n[muted]Install with: djinn plugin install <name>[/muted]\n")
    
    elif action == "list":
        installed = marketplace.list_installed()
        if installed:
            console.print("\n[highlight]Installed Plugins[/highlight]\n")
            for name, info in installed.items():
                console.print(f"  [success]{name}[/success] v{info.get('version', '?')}")
            console.print()
        else:
            console.print("[muted]No plugins installed.[/muted]")
    
    elif action == "install":
        if not plugin_name:
            console.print("[error]Usage: djinn plugin install <name>[/error]")
            return
        with spinner.status(f"Installing {plugin_name}..."):
            success = marketplace.install(plugin_name)
        if success:
            console.print(f"[success]Installed {plugin_name}![/success]")
        else:
            console.print(f"[error]Plugin '{plugin_name}' not found.[/error]")
    
    elif action == "uninstall":
        if marketplace.uninstall(plugin_name):
            console.print(f"[success]Uninstalled {plugin_name}.[/success]")
        else:
            console.print(f"[error]Plugin '{plugin_name}' not installed.[/error]")


@main.command()
@click.argument("commands", nargs=-1, required=True)
def chain(commands):
    """Chain multiple commands together.
    
    Use + to separate commands. AI will generate the proper chained command.
    
    Examples:
        djinn chain "build" + "test" + "deploy"
        djinn chain "git pull" + "npm install" + "npm start"
    """
    # Parse commands separated by +
    cmd_list = " ".join(commands).split("+")
    cmd_list = [c.strip().strip('"').strip("'") for c in cmd_list if c.strip()]
    
    if len(cmd_list) < 2:
        console.print("[error]Need at least 2 commands to chain. Use + to separate.[/error]")
        return
    
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
    analyzer = ContextAnalyzer()
    
    console.print(f"\n[prompt]> Chaining {len(cmd_list)} commands:[/prompt]")
    for i, cmd in enumerate(cmd_list, 1):
        console.print(f"  {i}. {cmd}")
    console.print()
    
    shell_info = analyzer.get_shell_info()
    prompt = f"""Generate a single chained command that performs these actions in sequence:
{chr(10).join(f'{i}. {c}' for i, c in enumerate(cmd_list, 1))}

Shell: {shell_info}
Use && for sequential execution. Output only the chained command."""
    
    with spinner.status("Generating chained command..."):
        result = engine.backend.generate(prompt, "You are a shell expert. Chain commands properly using && or ;")
    
    if result:
        spinner.print_success(result)
        try:
            pyperclip.copy(result)
            spinner.print_copied()
        except:
            pass
    else:
        console.print("[error]Failed to generate chained command.[/error]")


@main.command()
@click.argument("query", nargs=-1, required=True)
def web(query):
    """Search the web for command help.
    
    Generates a command based on web knowledge for common tools.
    
    Examples:
        djinn web "how to install docker on ubuntu"
        djinn web "ffmpeg convert mp4 to gif"
    """
    query_text = " ".join(query)
    config = load_config()
    engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
    
    console.print(f"\n[prompt]> Web Search:[/prompt] {query_text}")
    console.print("[muted]" + "=" * 50 + "[/muted]")
    
    # Enhanced prompt for web-like knowledge
    prompt = f"""Web query: {query_text}

Based on common documentation and StackOverflow answers, provide:
1. The exact command(s) to run
2. A brief explanation

Be specific and practical. Use latest best practices."""
    
    with spinner.status("Searching knowledge base..."):
        result = engine.backend.generate(prompt, 
            "You are a helpful assistant with access to documentation for all major CLI tools, package managers, and DevOps tools. Provide practical, tested commands.")
    
    if result:
        console.print(f"\n[success]Result:[/success]\n")
        console.print(result)
        console.print()
    else:
        console.print("[error]No results found.[/error]")


@main.command()
def tour():
    """Interactive tour of DJINN features.
    
    Learn about all the powerful features DJINN offers.
    """
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    tour_content = """
# 🧞‍♂️ Welcome to the DJINN Tour!

DJINN is your AI-powered terminal assistant with **87+ specialized commands**.

## 🚀 Quick Start
```bash
djinn "list all files larger than 100MB"  # Generate command
djinn -x "create backup folder"            # Execute directly
djinn -i                                   # Interactive mode
```

## ⚡ Key Features

1. **Deep Context** - DJINN reads your project files for smarter suggestions
2. **Auto-Fix** - Failed commands? DJINN suggests fixes automatically
3. **Plugins** - 87+ specialized plugins (git, docker, k8s, aws, etc.)
4. **Themes** - 12 beautiful color themes

## 🛠️ Power User Commands

- `djinn stats` - View your usage statistics
- `djinn vault add` - Store sensitive commands securely
- `djinn chain` - Chain multiple commands together
- `djinn redo` - Re-run with modifications
- `djinn plugin available` - Browse community plugins

## 🎨 Customize

```bash
djinn theme dracula    # Change theme
djinn alias add deploy "build and deploy to prod"
djinn config --show    # View settings
```

Press Enter to continue...
"""
    
    Logo.print_logo(console, mini=True)
    console.print(Panel(Markdown(tour_content), title="🎓 DJINN Tour", border_style="green"))
    input()
    console.print("[success]You're all set! Try running:[/success] djinn \"list all docker containers\"\n")


@main.command()
@click.argument("action", type=click.Choice(["list", "available", "download", "delete", "info", "recommend", "run"]))
@click.argument("model_name", required=False)
def model(action, model_name):
    """Download and manage local LLM models.
    
    Works with Ollama to download, list, and manage models.
    
    Examples:
        djinn model available            # Browse popular models
        djinn model list                 # Show installed models
        djinn model download llama3      # Download Llama 3
        djinn model download mistral     # Download Mistral
        djinn model delete llama3        # Remove a model
        djinn model info codellama       # Get model details
        djinn model recommend            # Get recommendations for your hardware
        djinn model run llama3           # Run model interactively
    """
    from djinn.core.models import ModelManager
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    mgr = ModelManager()
    
    # Check if Ollama is available
    if not mgr.check_ollama_available():
        console.print("\n[error]❌ Ollama is not running![/error]")
        console.print("\n[muted]To use local models, you need Ollama installed and running.[/muted]")
        console.print("\n[highlight]Quick Install:[/highlight]")
        console.print("  [prompt]Windows:[/prompt] winget install Ollama.Ollama")
        console.print("  [prompt]macOS:[/prompt]   brew install ollama")
        console.print("  [prompt]Linux:[/prompt]   curl -fsSL https://ollama.com/install.sh | sh")
        console.print("\n[muted]Then run: ollama serve[/muted]\n")
        return
    
    if action == "available":
        console.print("\n[highlight]🤖 Popular Models for Download[/highlight]\n")
        
        table = Table(border_style="green")
        table.add_column("Model", style="success", width=18)
        table.add_column("Sizes", style="command", width=20)
        table.add_column("Description", style="muted", width=45)
        
        for model_id, info in mgr.list_popular().items():
            sizes = ", ".join(info["sizes"])
            table.add_row(model_id, sizes, info["description"])
        
        console.print(table)
        console.print("\n[muted]Download with: djinn model download <model_name>[/muted]")
        console.print("[muted]Example: djinn model download llama3[/muted]\n")
    
    elif action == "list":
        installed = mgr.list_installed_ollama()
        
        if installed:
            console.print("\n[highlight]📦 Installed Models[/highlight]\n")
            
            table = Table(border_style="green")
            table.add_column("Model", style="success")
            table.add_column("Size", style="command")
            table.add_column("Modified", style="muted")
            
            for m in installed:
                size_gb = m.get("size", 0) / (1024**3)
                modified = m.get("modified_at", "")[:10] if m.get("modified_at") else ""
                table.add_row(m.get("name", "?"), f"{size_gb:.1f} GB", modified)
            
            console.print(table)
            console.print()
        else:
            console.print("\n[muted]No models installed yet.[/muted]")
            console.print("[muted]Run: djinn model download llama3[/muted]\n")
    
    elif action == "download":
        if not model_name:
            console.print("[error]Usage: djinn model download <model_name>[/error]")
            console.print("[muted]Example: djinn model download llama3[/muted]")
            return
        
        console.print(f"\n[highlight]⬇️ Downloading {model_name}...[/highlight]\n")
        console.print("[muted]This may take a while depending on model size and internet speed.[/muted]\n")
        
        def progress_callback(line):
            if line:
                console.print(f"  {line}")
        
        success = mgr.download_ollama(model_name, callback=progress_callback)
        
        if success:
            console.print(f"\n[success]✅ Successfully downloaded {model_name}![/success]")
            console.print(f"[muted]You can now use it with DJINN or run: djinn model run {model_name}[/muted]\n")
        else:
            console.print(f"\n[error]❌ Failed to download {model_name}[/error]")
            console.print("[muted]Make sure the model name is correct and Ollama is running.[/muted]\n")
    
    elif action == "delete":
        if not model_name:
            console.print("[error]Usage: djinn model delete <model_name>[/error]")
            return
        
        if Confirm.ask(f"[warning]Delete model '{model_name}'?[/warning]"):
            if mgr.delete_ollama(model_name):
                console.print(f"[success]Deleted {model_name}[/success]")
            else:
                console.print(f"[error]Failed to delete {model_name}[/error]")
    
    elif action == "info":
        if not model_name:
            console.print("[error]Usage: djinn model info <model_name>[/error]")
            return
        
        info = mgr.get_model_info(model_name)
        if info:
            console.print(f"\n[highlight]{info['name']}[/highlight]")
            console.print(f"[muted]{info['description']}[/muted]")
            console.print(f"\n[prompt]Available sizes:[/prompt] {', '.join(info['sizes'])}")
            console.print(f"[prompt]Recommended:[/prompt] {model_name}:{info['default_size']}")
            console.print(f"\n[muted]Download with: djinn model download {model_name}:{info['default_size']}[/muted]\n")
        else:
            console.print(f"[muted]No info available for '{model_name}'. It may still be downloadable.[/muted]")
            console.print(f"[muted]Try: djinn model download {model_name}[/muted]")
    
    elif action == "recommend":
        console.print("\n[highlight]💡 Model Recommendations[/highlight]\n")
        
        console.print("[prompt]Based on VRAM:[/prompt]\n")
        
        recommendations = [
            ("24+ GB", mgr.get_recommended_for_hardware(24)),
            ("12 GB", mgr.get_recommended_for_hardware(12)),
            ("8 GB", mgr.get_recommended_for_hardware(8)),
            ("6 GB", mgr.get_recommended_for_hardware(6)),
            ("4 GB or less", mgr.get_recommended_for_hardware(4)),
        ]
        
        for vram, models in recommendations:
            console.print(f"  [success]{vram}:[/success] {', '.join(models)}")
        
        console.print("\n[muted]Most popular starting point: djinn model download llama3[/muted]\n")
    
    elif action == "run":
        if not model_name:
            console.print("[error]Usage: djinn model run <model_name>[/error]")
            return
        
        console.print(f"\n[highlight]🚀 Starting {model_name}...[/highlight]")
        console.print("[muted]Type /bye to exit[/muted]\n")
        
        mgr.run_model_interactive(model_name)


# ============================================================================
# PRO FEATURES
# ============================================================================

@main.command()
@click.argument("topic", required=False)
@click.option("-s", "--search", help="Search across all cheatsheets")
def cheat(topic, search):
    """Built-in cheatsheets for popular CLI tools.
    
    Available: git, docker, kubernetes, linux, npm, python, aws, postgres
    
    Examples:
        djinn cheat                  # List available sheets
        djinn cheat git              # Show git cheatsheet
        djinn cheat docker           # Show docker cheatsheet
        djinn cheat -s "branch"      # Search all sheets
    """
    from djinn.core.cheatsheets import CheatsheetManager
    from rich.table import Table
    from rich.panel import Panel
    
    if search:
        results = CheatsheetManager.search(search)
        if results:
            console.print(f"\n[highlight]Search results for '{search}':[/highlight]\n")
            for sheet, section, cmd, desc in results:
                console.print(f"  [{sheet}] [success]{cmd}[/success]")
                console.print(f"       [muted]{desc}[/muted]")
            console.print()
        else:
            console.print(f"[muted]No results for '{search}'[/muted]")
        return
    
    if not topic:
        available = CheatsheetManager.list_available()
        console.print("\n[highlight]📚 Available Cheatsheets[/highlight]\n")
        for name in available:
            console.print(f"  [success]{name}[/success]")
        console.print("\n[muted]Usage: djinn cheat <topic>[/muted]\n")
        return
    
    sheet = CheatsheetManager.get(topic)
    if not sheet:
        console.print(f"[error]Cheatsheet '{topic}' not found.[/error]")
        console.print(f"[muted]Available: {', '.join(CheatsheetManager.list_available())}[/muted]")
        return
    
    console.print(f"\n[highlight]{sheet['title']}[/highlight]\n")
    
    for section, commands in sheet["sections"].items():
        console.print(f"[prompt]{section}[/prompt]")
        for cmd, desc in commands:
            console.print(f"  [command]{cmd}[/command]")
            console.print(f"    [muted]{desc}[/muted]")
        console.print()


@main.command()
@click.argument("action", type=click.Choice(["generate", "template", "list"]))
@click.argument("description", nargs=-1, required=False)
def compose(action, description):
    """Generate Docker Compose files.
    
    Examples:
        djinn compose list                           # List templates
        djinn compose template wordpress             # Use template
        djinn compose generate "node app with redis" # AI generates
    """
    from djinn.core.compose import ComposeGenerator
    
    if action == "list":
        gen = ComposeGenerator()
        templates = gen.list_templates()
        console.print("\n[highlight]🐳 Docker Compose Templates[/highlight]\n")
        for t in templates:
            console.print(f"  [success]{t}[/success]")
        console.print("\n[muted]Usage: djinn compose template <name>[/muted]\n")
        return
    
    if action == "template":
        if not description:
            console.print("[error]Usage: djinn compose template <name>[/error]")
            return
        
        template_name = " ".join(description)
        gen = ComposeGenerator()
        result = gen.get_template(template_name)
        
        if result:
            console.print(f"\n[highlight]docker-compose.yml for {template_name}:[/highlight]\n")
            from rich.syntax import Syntax
            syntax = Syntax(result, "yaml", theme="monokai")
            console.print(syntax)
            
            try:
                pyperclip.copy(result)
                spinner.print_copied()
            except:
                pass
        else:
            console.print(f"[error]Template '{template_name}' not found.[/error]")
        return
    
    if action == "generate":
        if not description:
            console.print("[error]Usage: djinn compose generate \"description\"[/error]")
            return
        
        desc_text = " ".join(description)
        config = load_config()
        engine = DjinnEngine(backend=config.get("backend", "ollama"), model=config.get("model"), api_key=config.get("api_key"))
        gen = ComposeGenerator(engine)
        
        console.print(f"\n[prompt]Generating docker-compose.yml for:[/prompt] {desc_text}\n")
        
        with spinner.status("Generating Docker Compose..."):
            result = gen.generate(desc_text)
        
        if result:
            from rich.syntax import Syntax
            syntax = Syntax(result, "yaml", theme="monokai")
            console.print(syntax)
            
            try:
                pyperclip.copy(result)
                spinner.print_copied()
            except:
                pass
        else:
            console.print("[error]Failed to generate compose file.[/error]")


@main.command()
@click.option("--fix", is_flag=True, help="Attempt to fix issues")
def scan(fix):
    """Scan dependencies for vulnerabilities and updates.
    
    Supports npm and pip projects.
    
    Examples:
        djinn scan         # Scan current project
        djinn scan --fix   # Attempt to fix issues
    """
    from djinn.core.scanner import DependencyScanner
    from rich.table import Table
    
    scanner = DependencyScanner()
    project_types = scanner.detect_project_type()
    
    if not project_types:
        console.print("[warning]No supported project files found.[/warning]")
        console.print("[muted]Supported: package.json, requirements.txt, pyproject.toml[/muted]")
        return
    
    console.print(f"\n[highlight]🔍 Scanning Dependencies[/highlight]")
    console.print(f"[muted]Detected: {', '.join(project_types)}[/muted]\n")
    
    results = scanner.full_scan()
    
    for pkg_mgr, data in results.get("scans", {}).items():
        console.print(f"[prompt]{pkg_mgr.upper()}[/prompt]\n")
        
        vulns = data.get("vulnerabilities", {})
        if vulns.get("error"):
            console.print(f"  [warning]{vulns['error']}[/warning]")
            if vulns.get("note"):
                console.print(f"  [muted]{vulns['note']}[/muted]")
        elif vulns.get("total", 0) > 0:
            console.print(f"  [error]⚠️ {vulns['total']} vulnerabilities found[/error]")
            if vulns.get("critical"):
                console.print(f"    Critical: {vulns['critical']}")
            if vulns.get("high"):
                console.print(f"    High: {vulns['high']}")
        else:
            console.print(f"  [success]✅ No known vulnerabilities[/success]")
        
        outdated = data.get("outdated", [])
        if outdated:
            console.print(f"\n  [warning]📦 {len(outdated)} outdated packages:[/warning]")
            for pkg in outdated[:5]:
                if isinstance(pkg, dict):
                    name = pkg.get("package", pkg.get("name", "?"))
                    current = pkg.get("current", pkg.get("version", "?"))
                    latest = pkg.get("latest", pkg.get("latest_version", "?"))
                    console.print(f"    {name}: {current} → {latest}")
            if len(outdated) > 5:
                console.print(f"    [muted]...and {len(outdated) - 5} more[/muted]")
        
        console.print()
    
    if fix:
        console.print("[muted]Running fix commands...[/muted]")
        if "npm" in project_types:
            subprocess.run(["npm", "audit", "fix"], cwd=str(scanner.directory))


@main.command()
@click.argument("action", type=click.Choice(["bump", "tag", "changelog", "info"]))
@click.argument("bump_type", type=click.Choice(["patch", "minor", "major"]), required=False)
def release(action, bump_type):
    """Automate Git releases and versioning.
    
    Examples:
        djinn release info                 # Show current version
        djinn release bump patch           # Bump patch version
        djinn release changelog            # Generate changelog
        djinn release tag                  # Create git tag
    """
    from djinn.core.release import ReleaseManager
    
    mgr = ReleaseManager()
    
    if action == "info":
        version = mgr.get_current_version()
        console.print(f"\n[highlight]Current Version:[/highlight] {version or 'Not found'}\n")
        
        commits = mgr.get_commits_since_tag()
        if commits:
            console.print(f"[prompt]Commits since last tag:[/prompt]")
            for c in commits[:10]:
                console.print(f"  {c}")
            if len(commits) > 10:
                console.print(f"  [muted]...and {len(commits) - 10} more[/muted]")
        console.print()
    
    elif action == "bump":
        if not bump_type:
            bump_type = "patch"
        
        old, new = mgr.bump_version(bump_type)
        console.print(f"\n[highlight]Version Bump ({bump_type}):[/highlight]")
        console.print(f"  {old} → [success]{new}[/success]\n")
        
        if Confirm.ask("Update version in project files?"):
            updated = mgr.update_version_files(new)
            if updated:
                console.print(f"[success]Updated: {', '.join(updated)}[/success]")
            else:
                console.print("[warning]No files updated[/warning]")
    
    elif action == "changelog":
        version = mgr.get_current_version() or "Unreleased"
        commits = mgr.get_commits_since_tag()
        
        if commits:
            entry = mgr.generate_changelog_entry(version, commits)
            console.print(f"\n[highlight]Generated Changelog Entry:[/highlight]\n")
            console.print(entry)
            
            try:
                pyperclip.copy(entry)
                spinner.print_copied()
            except:
                pass
        else:
            console.print("[muted]No commits since last tag.[/muted]")
    
    elif action == "tag":
        version = mgr.get_current_version()
        if not version:
            console.print("[error]Could not detect version.[/error]")
            return
        
        if Confirm.ask(f"Create tag v{version}?"):
            if mgr.create_tag(version):
                console.print(f"[success]Created tag v{version}[/success]")
                
                if Confirm.ask("Push tag to remote?"):
                    if mgr.push_tag(version):
                        console.print("[success]Tag pushed![/success]")
                    else:
                        console.print("[error]Failed to push tag[/error]")
            else:
                console.print("[error]Failed to create tag[/error]")


@main.command()
@click.argument("action", type=click.Choice(["export", "import"]))
@click.argument("file_path", required=False)
def sync(action, file_path):
    """Export or import DJINN settings.
    
    Examples:
        djinn sync export                    # Export to home directory
        djinn sync export ~/my-backup.json   # Export to specific file
        djinn sync import ~/backup.json      # Import settings
    """
    from djinn.core.sync import SyncManager
    
    mgr = SyncManager()
    
    if action == "export":
        output = mgr.export_settings(file_path)
        console.print(f"\n[success]✅ Settings exported to:[/success]")
        console.print(f"   {output}\n")
        console.print("[muted]Share this file to sync with another machine.[/muted]\n")
    
    elif action == "import":
        if not file_path:
            console.print("[error]Usage: djinn sync import <file>[/error]")
            return
        
        results = mgr.import_settings(file_path, merge=True)
        
        if results["imported"]:
            console.print(f"\n[success]✅ Imported:[/success] {', '.join(results['imported'])}")
        
        if results["errors"]:
            console.print(f"[error]Errors:[/error]")
            for e in results["errors"]:
                console.print(f"  {e}")
        
        console.print()


@main.command()
def predict():
    """Get smart command suggestions based on context.
    
    Analyzes your current directory and history to suggest useful commands.
    """
    from djinn.core.predictive import PredictiveEngine
    from djinn.core.context import ContextAnalyzer
    
    analyzer = ContextAnalyzer()
    context = analyzer.analyze()
    history = HistoryManager()
    
    engine = PredictiveEngine(history)
    
    console.print("\n[highlight]🔮 Smart Suggestions[/highlight]\n")
    
    # Based on directory
    files = context.get("files", [])
    dir_suggestions = engine.suggest_for_directory(files)
    if dir_suggestions:
        console.print("[prompt]Based on this directory:[/prompt]")
        for s in dir_suggestions:
            console.print(f"  [command]{s}[/command]")
        console.print()
    
    # Most frequent
    freq = engine.get_frequent_commands(5)
    if freq:
        console.print("[prompt]Your most used commands:[/prompt]")
        for s in freq:
            console.print(f"  [command]{s}[/command]")
        console.print()
    
    # Context-based
    recent = history.get_recent(1)
    if recent:
        last_cmd = recent[0].get("command", "")
        next_cmds = engine.predict_next(last_cmd, files)
        if next_cmds:
            console.print(f"[prompt]After '{last_cmd[:30]}...':[/prompt]")
            for s in next_cmds:
                console.print(f"  [command]{s}[/command]")
            console.print()


@main.command()
@click.argument("message", nargs=-1, required=True)
def notify(message):
    """Send a desktop notification.
    
    Useful for alerting when long commands complete.
    
    Examples:
        djinn notify "Build complete!"
        long_command && djinn notify "Done!"
    """
    from djinn.core.notifications import NotificationManager
    
    msg = " ".join(message)
    
    success = NotificationManager.notify("DJINN", msg, sound=True)
    
    if success:
        console.print(f"[success]🔔 Notification sent![/success]")
    else:
        console.print(f"[warning]Could not send notification, but here's your message:[/warning]")
        console.print(f"[highlight]{msg}[/highlight]")


# ============================================================================
# INNOVATIVE FEATURES
# ============================================================================

@main.command()
@click.argument("action", type=click.Choice(["status", "shortcut", "insights"]))
@click.argument("args", nargs=-1)
def learn(action, args):
    """Learn from your patterns and create shortcuts.
    
    Examples:
        djinn learn status              # View learning status
        djinn learn shortcut add deploy "deploy to production"
        djinn learn shortcut list       # List shortcuts
        djinn learn insights            # View usage insights
    """
    from djinn.core.learning import LearningEngine
    
    engine = LearningEngine()
    
    if action == "status":
        insights = engine.get_insights()
        console.print("\n[highlight]🧠 Learning Status[/highlight]\n")
        console.print(f"  Sequences learned: {insights['total_sequences']}")
        console.print(f"  Shortcuts saved: {insights['total_shortcuts']}")
        console.print()
    
    elif action == "shortcut":
        if not args:
            # List shortcuts
            shortcuts = engine.list_shortcuts()
            if shortcuts:
                console.print("\n[highlight]Your Shortcuts[/highlight]\n")
                for name, prompt in shortcuts.items():
                    console.print(f"  [success]{name}[/success]: {prompt[:50]}")
            else:
                console.print("[muted]No shortcuts saved yet.[/muted]")
        elif args[0] == "add" and len(args) >= 3:
            name = args[1]
            prompt = " ".join(args[2:])
            engine.add_shortcut(name, prompt)
            console.print(f"[success]Shortcut '{name}' saved![/success]")
        elif args[0] == "get" and len(args) >= 2:
            prompt = engine.get_shortcut(args[1])
            if prompt:
                console.print(f"[success]{prompt}[/success]")
            else:
                console.print("[muted]Shortcut not found.[/muted]")
    
    elif action == "insights":
        insights = engine.get_insights()
        console.print("\n[highlight]📊 Usage Insights[/highlight]\n")
        console.print(f"  Active times: {', '.join(insights['active_times'][:5])}")
        console.print(f"  Project types: {', '.join(insights['directory_types'][:5])}")
        console.print()


@main.command()
@click.argument("action", type=click.Choice(["create", "list", "run", "delete", "templates"]))
@click.argument("name", required=False)
@click.option("--dry-run", is_flag=True, help="Show what would run without executing")
def flow(action, name, dry_run):
    """Create and run multi-step workflows.
    
    Examples:
        djinn flow templates            # List built-in templates
        djinn flow create my-deploy     # Create new workflow
        djinn flow list                 # List workflows
        djinn flow run my-deploy        # Run a workflow
        djinn flow run my-deploy --dry-run
    """
    from djinn.core.workflow import WorkflowEngine, WORKFLOW_TEMPLATES
    
    engine = WorkflowEngine()
    
    if action == "templates":
        console.print("\n[highlight]📋 Workflow Templates[/highlight]\n")
        for name, steps in WORKFLOW_TEMPLATES.items():
            console.print(f"  [success]{name}[/success]")
            for step in steps:
                console.print(f"    • {step['name']}: {step['command'][:40]}")
            console.print()
    
    elif action == "list":
        workflows = engine.list_all()
        if workflows:
            console.print("\n[highlight]Your Workflows[/highlight]\n")
            for w in workflows:
                console.print(f"  [success]{w}[/success]")
        else:
            console.print("[muted]No workflows yet. Use 'djinn flow create <name>'[/muted]")
    
    elif action == "create":
        if not name:
            console.print("[error]Usage: djinn flow create <name>[/error]")
            return
        
        console.print(f"\n[highlight]Creating workflow: {name}[/highlight]")
        console.print("[muted]Enter commands (empty line to finish):[/muted]\n")
        
        commands = []
        while True:
            cmd = console.input("[prompt]> [/prompt]")
            if not cmd:
                break
            commands.append(cmd)
        
        if commands:
            engine.create_from_commands(name, commands)
            console.print(f"\n[success]✅ Workflow '{name}' created with {len(commands)} steps![/success]")
    
    elif action == "run":
        if not name:
            console.print("[error]Usage: djinn flow run <name>[/error]")
            return
        
        console.print(f"\n[highlight]Running workflow: {name}[/highlight]\n")
        
        if dry_run:
            console.print("[muted]DRY RUN - commands will not execute[/muted]\n")
        
        result = engine.run(name, dry_run=dry_run)
        
        if "error" in result:
            console.print(f"[error]{result['error']}[/error]")
            return
        
        for step in result["steps"]:
            status_icon = "✅" if step["status"] == "success" else "❌" if "fail" in step["status"] else "⏭️"
            console.print(f"  {status_icon} {step['name']}: {step['status']}")
        
        if result["success"]:
            console.print(f"\n[success]✅ Workflow completed successfully![/success]")
        else:
            console.print(f"\n[error]Workflow failed.[/error]")
    
    elif action == "delete":
        if name and engine.delete(name):
            console.print(f"[success]Deleted workflow '{name}'[/success]")
        else:
            console.print("[error]Workflow not found.[/error]")


@main.command()
@click.argument("action", type=click.Choice(["list", "get", "set", "delete", "backup", "validate"]))
@click.argument("args", nargs=-1)
def env(action, args):
    """Manage .env files.
    
    Examples:
        djinn env list                  # List all variables
        djinn env get API_KEY           # Get a variable
        djinn env set API_KEY value     # Set a variable
        djinn env backup                # Backup .env
        djinn env validate              # Validate .env file
    """
    from djinn.core.environment import EnvManager
    
    mgr = EnvManager()
    
    if action == "list":
        env_vars = mgr.list_all()
        if env_vars:
            console.print("\n[highlight]Environment Variables[/highlight]\n")
            for key, value in env_vars.items():
                # Mask sensitive values
                if any(s in key.lower() for s in ["secret", "password", "key", "token"]):
                    display_val = value[:3] + "***" if len(value) > 3 else "***"
                else:
                    display_val = value[:40] + "..." if len(value) > 40 else value
                console.print(f"  [success]{key}[/success]={display_val}")
        else:
            console.print("[muted]No .env file found.[/muted]")
    
    elif action == "get" and args:
        value = mgr.get(args[0])
        if value:
            console.print(f"[success]{value}[/success]")
        else:
            console.print("[muted]Variable not found.[/muted]")
    
    elif action == "set" and len(args) >= 2:
        mgr.set(args[0], " ".join(args[1:]))
        console.print(f"[success]Set {args[0]}[/success]")
    
    elif action == "delete" and args:
        if mgr.delete(args[0]):
            console.print(f"[success]Deleted {args[0]}[/success]")
        else:
            console.print("[muted]Variable not found.[/muted]")
    
    elif action == "backup":
        path = mgr.backup()
        if path:
            console.print(f"[success]Backed up to: {path}[/success]")
        else:
            console.print("[error]No .env file to backup.[/error]")
    
    elif action == "validate":
        result = mgr.validate()
        if result["valid"]:
            console.print("[success]✅ .env file is valid![/success]")
        else:
            console.print("[error].env has issues:[/error]")
            for issue in result["issues"]:
                console.print(f"  • {issue}")


@main.command()
@click.argument("action", type=click.Choice(["start", "stop", "list", "export", "delete"]))
@click.argument("name", required=False)
def record(action, name):
    """Record terminal sessions.
    
    Examples:
        djinn record start my-session   # Start recording
        djinn record stop               # Stop and save
        djinn record list               # List recordings
        djinn record export my-session  # Export to script
    """
    from djinn.core.recorder import TerminalRecorder
    
    recorder = TerminalRecorder()
    
    if action == "start":
        session_name = recorder.start(name)
        console.print(f"[success]🎬 Recording started: {session_name}[/success]")
        console.print("[muted]Use 'djinn record stop' to finish[/muted]")
    
    elif action == "stop":
        path = recorder.stop()
        if path:
            console.print(f"[success]✅ Recording saved: {path}[/success]")
        else:
            console.print("[muted]No active recording.[/muted]")
    
    elif action == "list":
        recordings = recorder.list_recordings()
        if recordings:
            console.print("\n[highlight]Recordings[/highlight]\n")
            for r in recordings:
                console.print(f"  [success]{r['name']}[/success] ({r['commands']} commands)")
        else:
            console.print("[muted]No recordings yet.[/muted]")
    
    elif action == "export" and name:
        path = recorder.export_to_script(name)
        if path:
            console.print(f"[success]Exported to: {path}[/success]")
        else:
            console.print("[error]Recording not found.[/error]")
    
    elif action == "delete" and name:
        if recorder.delete_recording(name):
            console.print(f"[success]Deleted: {name}[/success]")
        else:
            console.print("[error]Recording not found.[/error]")


@main.command()
@click.argument("action", type=click.Choice(["readme", "script", "api"]))
@click.argument("file_path", required=False)
def docs(action, file_path):
    """Auto-generate documentation.
    
    Examples:
        djinn docs readme               # Generate README
        djinn docs script myscript.sh   # Document a script
        djinn docs api mymodule.py      # Generate API docs
    """
    from djinn.core.docs import DocsGenerator
    
    gen = DocsGenerator()
    
    if action == "readme":
        doc = gen.generate_readme()
        console.print(doc)
        
        if Confirm.ask("Save as README.md?"):
            with open("README.md", "w") as f:
                f.write(doc)
            console.print("[success]Saved README.md[/success]")
    
    elif action == "script" and file_path:
        doc = gen.generate_for_script(file_path)
        console.print(doc)
    
    elif action == "api" and file_path:
        doc = gen.generate_api_docs(file_path)
        console.print(doc)


@main.command("why")
@click.argument("error_message", nargs=-1)
def why_cmd(error_message):
    """Explain WHY a command failed.
    
    Example:
        djinn why "permission denied"
    """
    from djinn.core.docs import WhyExplainer
    
    error = " ".join(error_message)
    explainer = WhyExplainer()
    
    explanation = explainer.explain("", error)
    console.print(explanation)


@main.command()
@click.argument("action", type=click.Choice(["add", "list", "run", "cancel"]))
@click.argument("args", nargs=-1)
def schedule(action, args):
    """Schedule commands to run later.
    
    Examples:
        djinn schedule add "npm test" +1h     # Run in 1 hour
        djinn schedule add "backup" +30m      # Run in 30 minutes
        djinn schedule list                   # List pending
        djinn schedule run                    # Run due tasks
    """
    from djinn.core.scheduler import Scheduler
    
    sched = Scheduler()
    
    if action == "add" and len(args) >= 2:
        command = args[0]
        run_at = args[1]
        task = sched.add(command, run_at)
        console.print(f"[success]✅ Scheduled: {task['name']}[/success]")
        console.print(f"   Will run at: {task['run_at']}")
    
    elif action == "list":
        tasks = sched.list_pending()
        if tasks:
            console.print("\n[highlight]Pending Tasks[/highlight]\n")
            for t in tasks:
                console.print(f"  [{t['id']}] {t['name']}: {t['command'][:30]}")
                console.print(f"      Run at: {t['run_at']}")
        else:
            console.print("[muted]No pending tasks.[/muted]")
    
    elif action == "run":
        results = sched.run_due()
        if results:
            console.print(f"[success]Ran {len(results)} tasks[/success]")
        else:
            console.print("[muted]No tasks due.[/muted]")
    
    elif action == "cancel" and args:
        task_id = int(args[0])
        if sched.cancel(task_id):
            console.print(f"[success]Cancelled task {task_id}[/success]")
        else:
            console.print("[error]Task not found.[/error]")


@main.command()
@click.argument("game_type", type=click.Choice(["typing", "quiz", "memory"]))
def game(game_type):
    """Play terminal games to learn CLI commands.
    
    Examples:
        djinn game typing    # Typing speed practice
        djinn game quiz      # CLI knowledge quiz
        djinn game memory    # Command memory game
    """
    from djinn.core.games import TypingGame, CLIQuiz, CommandMemory
    import time
    
    if game_type == "typing":
        game_instance = TypingGame()
        console.print("\n[highlight]⌨️ CLI Typing Challenge[/highlight]")
        console.print("[muted]Type the commands as fast as you can![/muted]\n")
        
        for _ in range(5):
            challenge = game_instance.get_challenge()
            console.print(f"[command]{challenge}[/command]")
            
            start = time.time()
            answer = console.input("[prompt]> [/prompt]")
            elapsed = time.time() - start
            
            result = game_instance.check_answer(challenge, answer, elapsed)
            
            if result["correct"]:
                console.print(f"[success]✅ Correct! {result['wpm']} WPM[/success]\n")
            else:
                console.print(f"[error]❌ Try again[/error]\n")
        
        stats = game_instance.get_stats()
        console.print(f"\n[highlight]Final Score: {stats['score']}/{stats['rounds']}[/highlight]")
        console.print(f"Accuracy: {stats['accuracy']}")
    
    elif game_type == "quiz":
        quiz = CLIQuiz()
        console.print("\n[highlight]🎓 CLI Knowledge Quiz[/highlight]\n")
        
        for _ in range(5):
            q = quiz.get_question()
            if not q:
                break
            
            console.print(f"[prompt]{q['q']}[/prompt]\n")
            for i, opt in enumerate(q["options"]):
                console.print(f"  {i+1}. {opt}")
            
            try:
                answer = int(console.input("\n[prompt]Your answer (1-4): [/prompt]")) - 1
                result = quiz.answer(q["index"], answer)
                
                if result["correct"]:
                    console.print(f"[success]✅ Correct![/success]")
                else:
                    console.print(f"[error]❌ Wrong. Answer: {result['correct_answer']}[/error]")
                console.print(f"[muted]{result['explanation']}[/muted]\n")
            except:
                console.print("[error]Invalid input[/error]")
        
        score = quiz.get_score()
        console.print(f"\n[highlight]Final Score: {score['score']}/{score['total']} ({score['percentage']})[/highlight]")
    
    elif game_type == "memory":
        console.print("\n[highlight]🧠 Command Memory Game[/highlight]")
        console.print("[muted]Match commands with their descriptions![/muted]\n")
        console.print("[muted]Coming in next update...[/muted]")


@main.command()
@click.argument("text", nargs=-1, required=True)
def speak(text):
    """Text-to-speech notification.
    
    Examples:
        djinn speak "Build complete!"
        long_command && djinn speak "Done!"
    """
    from djinn.core.visualizer import SpeechSynthesis
    
    message = " ".join(text)
    
    if SpeechSynthesis.speak(message):
        console.print(f"[success]🔊 Spoke: {message}[/success]")
    else:
        console.print(f"[warning]TTS not available. Message: {message}[/warning]")


@main.command()
@click.argument("action", type=click.Choice(["new", "list"]))
@click.argument("template", required=False)
def setup(action, template):
    """Quick project setup from templates.
    
    Examples:
        djinn setup list                # List templates
        djinn setup new node            # Setup Node.js project
        djinn setup new python          # Setup Python project
        djinn setup new fastapi         # Setup FastAPI project
    """
    from djinn.core.visualizer import ProjectSetup
    
    if action == "list":
        templates = ProjectSetup.list_templates()
        console.print("\n[highlight]📦 Project Templates[/highlight]\n")
        for t in templates:
            info = ProjectSetup.get_template(t)
            console.print(f"  [success]{t}[/success] - {info.get('name', '')}")
        console.print("\n[muted]Usage: djinn setup new <template>[/muted]\n")
    
    elif action == "new" and template:
        tmpl = ProjectSetup.get_template(template)
        if not tmpl:
            console.print(f"[error]Template '{template}' not found.[/error]")
            return
        
        console.print(f"\n[highlight]Setting up: {tmpl['name']}[/highlight]\n")
        
        # Create files
        for filename, content in tmpl.get("files", {}).items():
            with open(filename, "w") as f:
                f.write(content)
            console.print(f"  ✅ Created {filename}")
        
        # Run commands
        for cmd in tmpl.get("commands", []):
            console.print(f"  🔄 Running: {cmd}")
            subprocess.run(cmd, shell=True, capture_output=True)
        
        console.print(f"\n[success]✅ {tmpl['name']} setup complete![/success]")


@main.command()
@click.argument("action", type=click.Choice(["backup", "restore", "list", "export"]))
def dotfiles(action):
    """Backup and restore dotfiles.
    
    Examples:
        djinn dotfiles backup     # Backup dotfiles
        djinn dotfiles restore    # Restore dotfiles
        djinn dotfiles list       # List backed up files
        djinn dotfiles export     # Export as archive
    """
    from djinn.core.environment import DotfilesManager
    
    mgr = DotfilesManager()
    
    if action == "backup":
        result = mgr.backup()
        console.print("\n[highlight]Dotfiles Backup[/highlight]\n")
        console.print(f"  ✅ Backed up: {len(result['backed_up'])} files")
        for f in result['backed_up']:
            console.print(f"     • {f}")
        if result['skipped']:
            console.print(f"  ⏭️ Skipped: {len(result['skipped'])} files")
    
    elif action == "restore":
        result = mgr.restore()
        console.print("\n[highlight]Dotfiles Restored[/highlight]\n")
        console.print(f"  ✅ Restored: {len(result['restored'])} files")
    
    elif action == "list":
        files = mgr.list_backed_up()
        console.print("\n[highlight]Backed Up Dotfiles[/highlight]\n")
        for f in files:
            console.print(f"  • {f}")
    
    elif action == "export":
        path = mgr.export_archive()
        console.print(f"[success]Exported to: {path}[/success]")


@main.command()
@click.argument("command_text", nargs=-1, required=True)
def gist(command_text):
    """Share a command as GitHub Gist.
    
    Requires GITHUB_TOKEN environment variable.
    
    Example:
        djinn gist "my awesome script content"
    """
    from djinn.core.recorder import GistManager
    
    content = " ".join(command_text)
    mgr = GistManager()
    
    url = mgr.share_command(content)
    
    if url:
        console.print(f"[success]✅ Gist created: {url}[/success]")
        try:
            pyperclip.copy(url)
            console.print("[muted]URL copied to clipboard![/muted]")
        except:
            pass
    else:
        console.print("[error]Failed to create gist. Check GITHUB_TOKEN.[/error]")


# ============================================================================
# TUI & ADVANCED FEATURES (v2.0)
# ============================================================================

@main.command()
def dashboard():
    """Launch interactive system dashboard.
    
    Full-screen system monitor showing CPU, RAM, disk, network,
    and top processes in real-time.
    """
    try:
        from djinn.tui.dashboard import SystemDashboard
        
        console.print("[cyan]Launching System Dashboard...[/cyan]")
        console.print("[muted]Press Ctrl+C to exit[/muted]")
        
        dashboard = SystemDashboard()
        dashboard.run()
        
    except ImportError as e:
        console.print(f"[error]Missing dependency: {e}[/error]")
        console.print("[muted]Install psutil: pip install psutil[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@main.command()
@click.argument("action", type=click.Choice(["install", "uninstall", "list", "update", "outdated", "info"]))
@click.argument("package", required=False)
@click.option("--dev", "-D", is_flag=True, help="Install as dev dependency")
@click.option("--manager", "-m", help="Force specific package manager")
def pkg(action, package, dev, manager):
    """Universal package manager.
    
    Automatically detects project type and uses the right package manager.
    
    Examples:
        djinn pkg install requests       # Detects pip/npm/cargo
        djinn pkg install react -D       # Dev dependency
        djinn pkg list                   # List installed
        djinn pkg outdated               # Check outdated
    """
    from djinn.core.package_manager import UniversalPackageManager
    
    mgr = UniversalPackageManager()
    
    if action == "info":
        info = mgr.get_info()
        console.print(f"\n[highlight]Package Manager Info[/highlight]\n")
        console.print(f"  Directory: {info['directory']}")
        console.print(f"  Detected: [success]{info['manager'] or 'None'}[/success]")
        if info['lockfile']:
            console.print(f"  Lockfile: {info['lockfile']}")
        return
    
    detected = manager or mgr.detect_manager()
    if not detected and action not in ["info"]:
        console.print("[error]Could not detect package manager.[/error]")
        console.print("[muted]Make sure you're in a project directory or use --manager[/muted]")
        return
    
    console.print(f"[muted]Using: {detected}[/muted]")
    
    if action == "install":
        if not package:
            console.print("[error]Specify a package to install.[/error]")
            return
        console.print(f"[cyan]Installing {package}...[/cyan]")
        success, output = mgr.install(package, dev=dev, manager=manager)
        console.print(output[:1000])
        if success:
            console.print(f"[success]✅ Installed {package}[/success]")
    
    elif action == "uninstall":
        if not package:
            console.print("[error]Specify a package to uninstall.[/error]")
            return
        success, output = mgr.uninstall(package, manager=manager)
        console.print(output[:1000])
    
    elif action == "list":
        success, output = mgr.list_packages(manager=manager)
        console.print(output[:2000])
    
    elif action == "update":
        success, output = mgr.update(package, manager=manager)
        console.print(output[:1000])
    
    elif action == "outdated":
        success, output = mgr.outdated(manager=manager)
        console.print(output[:1000])


@main.command("db")
@click.argument("action", type=click.Choice(["connect", "tables", "query", "info"]))
@click.argument("args", nargs=-1)
def db_cmd(action, args):
    """Interactive database viewer.
    
    Examples:
        djinn db connect mydb.sqlite    # Connect to SQLite
        djinn db tables                 # List tables
        djinn db query "SELECT * FROM users LIMIT 10"
    """
    from djinn.tui.database import DatabaseViewer, SQLiteExplorer
    
    viewer = DatabaseViewer()
    
    if action == "connect":
        if not args:
            # Find SQLite databases
            dbs = SQLiteExplorer.find_databases()
            if dbs:
                console.print("\n[highlight]Found Databases[/highlight]\n")
                for db in dbs:
                    console.print(f"  • {db}")
            else:
                console.print("[muted]No SQLite databases found.[/muted]")
            return
        
        if viewer.connect_sqlite(args[0]):
            console.print(f"[success]Connected to {args[0]}[/success]")
            
            stats = viewer.get_stats()
            console.print(f"Tables: {stats['tables']}")
        else:
            console.print("[error]Could not connect.[/error]")
    
    elif action == "tables":
        if not args:
            console.print("[error]Connect first: djinn db connect <file>[/error]")
            return
        
        if viewer.connect_sqlite(args[0]):
            tables = viewer.list_tables()
            console.print("\n[highlight]Tables[/highlight]\n")
            for t in tables:
                count = viewer.count_rows(t)
                console.print(f"  📋 {t} ({count} rows)")
    
    elif action == "query":
        if len(args) < 2:
            console.print("[error]Usage: djinn db query <file> <sql>[/error]")
            return
        
        db_file = args[0]
        sql = " ".join(args[1:])
        
        if viewer.connect_sqlite(db_file):
            columns, rows = viewer.query(sql)
            table = viewer.render_results(columns, rows)
            console.print(table)
    
    elif action == "info":
        if args:
            info = SQLiteExplorer.quick_info(args[0])
            console.print(f"\n[highlight]Database: {info['path']}[/highlight]")
            console.print(f"  Size: {info.get('size_kb', 0):.1f} KB")
            console.print(f"  Tables: {info.get('tables', 0)}")


@main.command()
@click.argument("action", type=click.Choice(["get", "post", "put", "delete", "test"]))
@click.argument("url", required=False)
@click.option("--data", "-d", help="JSON data for POST/PUT")
@click.option("--header", "-H", multiple=True, help="Headers (key:value)")
def http(action, url, data, header):
    """Interactive HTTP client for API testing.
    
    Examples:
        djinn http get https://api.github.com
        djinn http post https://api.example.com/users -d '{"name":"John"}'
        djinn http get https://api.example.com -H "Authorization:Bearer token"
    """
    from djinn.tui.http_client import HTTPClient
    import json as json_lib
    
    client = HTTPClient()
    
    # Set headers
    for h in header:
        if ":" in h:
            key, value = h.split(":", 1)
            client.set_header(key.strip(), value.strip())
    
    # Parse data
    json_data = None
    if data:
        try:
            json_data = json_lib.loads(data)
        except:
            json_data = {"raw": data}
    
    if action == "get":
        response = client.get(url)
    elif action == "post":
        response = client.post(url, json_data)
    elif action == "put":
        response = client.put(url, json_data)
    elif action == "delete":
        response = client.delete(url)
    elif action == "test":
        console.print("[muted]API testing mode coming soon...[/muted]")
        return
    
    client.render_response(response)


@main.command()
@click.argument("path", required=False)
def explore(path):
    """Interactive file explorer.
    
    Examples:
        djinn explore           # Explore current directory
        djinn explore /var/log  # Explore specific path
    """
    from djinn.tui.file_explorer import FileExplorer
    
    explorer = FileExplorer(path)
    
    console.print(f"\n[highlight]📁 File Explorer[/highlight]")
    console.print(f"[muted]Path: {explorer.current_path}[/muted]")
    console.print(f"[muted]Commands: ls, cd <dir>, tree, q (quit)[/muted]\n")
    
    explorer.render_ls()
    
    while True:
        try:
            cmd = console.input("\n[prompt]explore> [/prompt]").strip()
            
            if not cmd or cmd == "q":
                break
            elif cmd == "ls":
                explorer.render_ls()
            elif cmd == "ls -a":
                explorer.render_ls(show_hidden=True)
            elif cmd.startswith("cd "):
                target = cmd[3:].strip()
                if explorer.cd(target):
                    console.print(f"[success]→ {explorer.current_path}[/success]")
                else:
                    console.print("[error]Invalid path[/error]")
            elif cmd == "tree":
                console.print(explorer.tree())
            elif cmd.startswith("mkdir "):
                name = cmd[6:].strip()
                if explorer.mkdir(name):
                    console.print(f"[success]Created {name}[/success]")
            elif cmd.startswith("rm "):
                name = cmd[3:].strip()
                if explorer.rm(name):
                    console.print(f"[success]Removed {name}[/success]")
            elif cmd == "pwd":
                console.print(str(explorer.current_path))
            else:
                console.print("[muted]Unknown command[/muted]")
                
        except KeyboardInterrupt:
            break


@main.command()
@click.option("--listen", is_flag=True, help="Start continuous listening")
def voice(listen):
    """Voice control for DJINN.
    
    Control your terminal with voice commands.
    Requires: pip install SpeechRecognition pyaudio
    
    Examples:
        djinn voice              # Single command
        djinn voice --listen     # Continuous mode
    """
    from djinn.core.advanced import VoiceController
    
    controller = VoiceController()
    
    if not controller.is_available():
        console.print("[error]Speech recognition not available.[/error]")
        console.print("[muted]Install: pip install SpeechRecognition pyaudio[/muted]")
        return
    
    if listen:
        controller.start_listening()
    else:
        text = controller.listen_once()
        if text:
            console.print(f"[cyan]Heard: {text}[/cyan]")
            controller.execute_voice_command(text)


@main.command()
@click.argument("target", required=False)
@click.option("--staged", is_flag=True, help="Review staged changes only")
def review(target, staged):
    """AI-powered code review.
    
    Review your code changes before committing.
    
    Examples:
        djinn review              # Review uncommitted changes
        djinn review --staged     # Review staged changes only
        djinn review file.py      # Review specific file
    """
    from djinn.core.advanced import AICodeReviewer
    
    reviewer = AICodeReviewer()
    
    if target:
        console.print(f"[cyan]Reviewing {target}...[/cyan]\n")
        result = reviewer.review_file(target)
    elif staged:
        console.print("[cyan]Reviewing staged changes...[/cyan]\n")
        result = reviewer.review_staged_changes()
    else:
        console.print("[cyan]Reviewing uncommitted changes...[/cyan]\n")
        result = reviewer.review_current_changes()
    
    console.print(result)


@main.command()
@click.argument("action", type=click.Choice(["list", "create", "stacks"]))
@click.argument("args", nargs=-1)
def architect(action, args):
    """Generate complex project architectures.
    
    Examples:
        djinn architect list                    # List architectures
        djinn architect stacks                  # List quick stacks
        djinn architect create fullstack-react-node myapp
    """
    from djinn.core.architect import ProjectArchitect, StackGenerator
    
    if action == "list":
        archs = ProjectArchitect.list_architectures()
        console.print("\n[highlight]📐 Project Architectures[/highlight]\n")
        for arch in archs:
            console.print(f"  [success]{arch['id']}[/success]")
            console.print(f"    {arch['description']}")
            console.print()
    
    elif action == "stacks":
        stacks = StackGenerator.list_stacks()
        console.print("\n[highlight]⚡ Quick Stacks[/highlight]\n")
        for stack in stacks:
            console.print(f"  [success]{stack['id']}[/success] - {stack['name']}")
    
    elif action == "create":
        if len(args) < 2:
            console.print("[error]Usage: djinn architect create <arch> <name>[/error]")
            return
        
        arch_id = args[0]
        name = args[1]
        
        architect = ProjectArchitect()
        
        console.print(f"[cyan]Creating {name} using {arch_id}...[/cyan]")
        
        if architect.create_project(arch_id, name):
            console.print(f"[success]✅ Created {name}![/success]")
            console.print(f"[muted]cd {name} to get started[/muted]")
        else:
            console.print("[error]Failed to create project.[/error]")


@main.command("ssh")
@click.argument("action", type=click.Choice(["list", "add", "connect", "keys"]))
@click.argument("args", nargs=-1)
def ssh_cmd(action, args):
    """SSH connection manager.
    
    Examples:
        djinn ssh list                          # List saved connections
        djinn ssh add myserver host user        # Add connection
        djinn ssh connect myserver              # Print connect command
        djinn ssh keys                          # List SSH keys
    """
    from djinn.core.advanced import SSHManager
    
    mgr = SSHManager()
    
    if action == "list":
        connections = mgr.list_connections()
        if connections:
            console.print("\n[highlight]SSH Connections[/highlight]\n")
            for conn in connections:
                console.print(f"  [success]{conn['alias']}[/success]")
                if 'hostname' in conn:
                    console.print(f"    → {conn.get('user', 'root')}@{conn['hostname']}")
        else:
            console.print("[muted]No saved connections. Add with: djinn ssh add <alias> <host> <user>[/muted]")
    
    elif action == "add":
        if len(args) < 3:
            console.print("[error]Usage: djinn ssh add <alias> <hostname> <user>[/error]")
            return
        
        alias, hostname, user = args[0], args[1], args[2]
        if mgr.add_connection(alias, hostname, user):
            console.print(f"[success]Added {alias}[/success]")
            console.print(f"[muted]Connect with: ssh {alias}[/muted]")
    
    elif action == "connect":
        if not args:
            console.print("[error]Specify connection alias.[/error]")
            return
        
        cmd = mgr.connect(args[0])
        console.print(f"[command]{cmd}[/command]")
    
    elif action == "keys":
        keys = mgr.list_keys()
        console.print("\n[highlight]SSH Keys[/highlight]\n")
        for key in keys:
            console.print(f"  🔑 {key}")


if __name__ == "__main__":
    main()
