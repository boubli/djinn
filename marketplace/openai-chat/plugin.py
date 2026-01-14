"""
OpenAI Plugin for DJINN
Direct ChatGPT/GPT-4 access from terminal.
"""
import click
from rich.console import Console
from rich.markdown import Markdown
import os
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "openai-chat"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Direct GPT-4/ChatGPT access from terminal."

CONFIG_FILE = Path.home() / ".djinn" / "openai.json"
HISTORY_FILE = Path.home() / ".djinn" / "chat_history.json"


def get_openai_client():
    """Get OpenAI client."""
    try:
        from openai import OpenAI
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE) as f:
                    api_key = json.load(f).get("api_key")
        
        if not api_key:
            console.print("[error]OPENAI_API_KEY not set[/error]")
            console.print("[muted]Run: djinn gpt auth YOUR_API_KEY[/muted]")
            return None
        
        return OpenAI(api_key=api_key)
    except ImportError:
        console.print("[error]openai not installed. Run: pip install openai[/error]")
        return None


def load_history():
    """Load conversation history."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []


def save_history(history):
    """Save conversation history."""
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    # Keep last 50 messages
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-50:], f, indent=2)


@click.group()
def gpt():
    """OpenAI GPT commands."""
    pass


@gpt.command(name="auth")
@click.argument("api_key")
def set_auth(api_key):
    """Save OpenAI API key."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"api_key": api_key}, f)
    
    console.print("[success]✓ OpenAI API key saved![/success]")


@gpt.command(name="ask")
@click.argument("prompt", nargs=-1, required=True)
@click.option("--model", default="gpt-4o-mini", help="Model to use")
@click.option("--system", help="System prompt")
@click.option("--temperature", default=0.7, type=float)
@click.option("--max-tokens", default=1000, type=int)
def ask(prompt, model, system, temperature, max_tokens):
    """Ask GPT a question."""
    client = get_openai_client()
    if not client:
        return
    
    prompt_text = " ".join(prompt)
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt_text})
    
    console.print(f"\n[bold cyan]🤖 {model}[/bold cyan]\n")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        
        print("\n")
        
        # Save to history
        history = load_history()
        history.append({"role": "user", "content": prompt_text})
        history.append({"role": "assistant", "content": full_response})
        save_history(history)
    except Exception as e:
        console.print(f"\n[error]Error: {e}[/error]")


@gpt.command(name="chat")
@click.option("--model", default="gpt-4o-mini")
@click.option("--system", help="System prompt")
def interactive_chat(model, system):
    """Start interactive chat session."""
    client = get_openai_client()
    if not client:
        return
    
    console.print(f"\n[bold cyan]🤖 Chat with {model}[/bold cyan]")
    console.print("[muted]Type 'exit' to quit, 'clear' to reset[/muted]\n")
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    
    while True:
        try:
            user_input = console.input("[bold green]You:[/bold green] ")
            
            if user_input.lower() == "exit":
                break
            elif user_input.lower() == "clear":
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                console.print("[muted]Chat cleared[/muted]\n")
                continue
            
            messages.append({"role": "user", "content": user_input})
            
            console.print(f"\n[bold cyan]GPT:[/bold cyan] ", end="")
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            print("\n")
            
            messages.append({"role": "assistant", "content": full_response})
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"\n[error]Error: {e}[/error]\n")
    
    # Save history
    save_history(messages)
    console.print("\n[muted]Chat ended[/muted]")


@gpt.command(name="code")
@click.argument("description", nargs=-1, required=True)
@click.option("--lang", default="python", help="Programming language")
@click.option("--model", default="gpt-4o-mini")
def generate_code(description, lang, model):
    """Generate code from description."""
    client = get_openai_client()
    if not client:
        return
    
    desc = " ".join(description)
    
    system = f"""You are a {lang} expert. Generate clean, well-commented code.
Only output the code, no explanations. Use best practices."""
    
    console.print(f"\n[bold cyan]💻 Generating {lang} code...[/bold cyan]\n")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": desc}
            ],
            temperature=0.3
        )
        
        code = response.choices[0].message.content
        
        from rich.syntax import Syntax
        syntax = Syntax(code, lang, theme="monokai")
        console.print(syntax)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@gpt.command(name="explain")
@click.argument("file_path")
@click.option("--model", default="gpt-4o-mini")
def explain_code(file_path, model):
    """Explain code in a file."""
    client = get_openai_client()
    if not client:
        return
    
    try:
        with open(file_path) as f:
            code = f.read()
        
        console.print(f"\n[bold cyan]📖 Explaining {file_path}...[/bold cyan]\n")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Explain this code clearly and concisely."},
                {"role": "user", "content": code[:4000]}
            ],
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        
        print("\n")
    except FileNotFoundError:
        console.print(f"[error]File not found: {file_path}[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@gpt.command(name="models")
def list_models():
    """List available models."""
    client = get_openai_client()
    if not client:
        return
    
    try:
        models = client.models.list()
        
        console.print("\n[bold cyan]🤖 Available Models[/bold cyan]\n")
        
        gpt_models = [m for m in models.data if "gpt" in m.id.lower()]
        gpt_models.sort(key=lambda m: m.id)
        
        for model in gpt_models[:20]:
            console.print(f"• {model.id}")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@gpt.command(name="image")
@click.argument("prompt", nargs=-1, required=True)
@click.option("--size", default="1024x1024")
@click.option("--output", default="generated_image.png")
def generate_image(prompt, size, output):
    """Generate an image with DALL-E."""
    client = get_openai_client()
    if not client:
        return
    
    prompt_text = " ".join(prompt)
    
    console.print(f"\n[bold cyan]🎨 Generating image...[/bold cyan]\n")
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_text,
            size=size,
            n=1
        )
        
        image_url = response.data[0].url
        
        # Download image
        import requests
        img_data = requests.get(image_url).content
        with open(output, 'wb') as f:
            f.write(img_data)
        
        console.print(f"[success]✓ Image saved to {output}[/success]")
        console.print(f"[muted]URL: {image_url}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = gpt

if __name__ == "__main__":
    gpt()
