"""
JSON/YAML Converter Plugin for DJINN
Convert between data formats.
"""
import click
from rich.console import Console
from rich.syntax import Syntax
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "data-converter"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Convert between JSON, YAML, TOML, CSV formats."


@click.group()
def convert():
    """Data format conversion commands."""
    pass


@convert.command(name="json2yaml")
@click.argument("input_file")
@click.option("--output", "-o", help="Output file")
def json_to_yaml(input_file, output):
    """Convert JSON to YAML."""
    try:
        import yaml
        
        with open(input_file) as f:
            data = json.load(f)
        
        yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        if output:
            with open(output, 'w') as f:
                f.write(yaml_str)
            console.print(f"[success]✓ Saved to {output}[/success]")
        else:
            syntax = Syntax(yaml_str, "yaml", theme="monokai")
            console.print(syntax)
    except ImportError:
        console.print("[error]pyyaml not installed. Run: pip install pyyaml[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@convert.command(name="yaml2json")
@click.argument("input_file")
@click.option("--output", "-o", help="Output file")
@click.option("--indent", default=2, type=int)
def yaml_to_json(input_file, output, indent):
    """Convert YAML to JSON."""
    try:
        import yaml
        
        with open(input_file) as f:
            data = yaml.safe_load(f)
        
        json_str = json.dumps(data, indent=indent, ensure_ascii=False)
        
        if output:
            with open(output, 'w') as f:
                f.write(json_str)
            console.print(f"[success]✓ Saved to {output}[/success]")
        else:
            syntax = Syntax(json_str, "json", theme="monokai")
            console.print(syntax)
    except ImportError:
        console.print("[error]pyyaml not installed. Run: pip install pyyaml[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@convert.command(name="json2toml")
@click.argument("input_file")
@click.option("--output", "-o", help="Output file")
def json_to_toml(input_file, output):
    """Convert JSON to TOML."""
    try:
        import toml
        
        with open(input_file) as f:
            data = json.load(f)
        
        toml_str = toml.dumps(data)
        
        if output:
            with open(output, 'w') as f:
                f.write(toml_str)
            console.print(f"[success]✓ Saved to {output}[/success]")
        else:
            syntax = Syntax(toml_str, "toml", theme="monokai")
            console.print(syntax)
    except ImportError:
        console.print("[error]toml not installed. Run: pip install toml[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@convert.command(name="toml2json")
@click.argument("input_file")
@click.option("--output", "-o", help="Output file")
def toml_to_json(input_file, output):
    """Convert TOML to JSON."""
    try:
        import toml
        
        with open(input_file) as f:
            data = toml.load(f)
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if output:
            with open(output, 'w') as f:
                f.write(json_str)
            console.print(f"[success]✓ Saved to {output}[/success]")
        else:
            syntax = Syntax(json_str, "json", theme="monokai")
            console.print(syntax)
    except ImportError:
        console.print("[error]toml not installed. Run: pip install toml[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@convert.command(name="csv2json")
@click.argument("input_file")
@click.option("--output", "-o", help="Output file")
def csv_to_json(input_file, output):
    """Convert CSV to JSON."""
    try:
        import csv
        
        with open(input_file, newline='') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if output:
            with open(output, 'w') as f:
                f.write(json_str)
            console.print(f"[success]✓ Saved to {output}[/success]")
        else:
            syntax = Syntax(json_str, "json", theme="monokai")
            console.print(syntax)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@convert.command(name="json2csv")
@click.argument("input_file")
@click.option("--output", "-o", help="Output file")
def json_to_csv(input_file, output):
    """Convert JSON array to CSV."""
    try:
        import csv
        
        with open(input_file) as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            console.print("[error]JSON must be an array of objects[/error]")
            return
        
        if not data:
            console.print("[error]Empty JSON array[/error]")
            return
        
        fieldnames = list(data[0].keys())
        
        if output:
            with open(output, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            console.print(f"[success]✓ Saved to {output}[/success]")
        else:
            import io
            output_str = io.StringIO()
            writer = csv.DictWriter(output_str, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            console.print(output_str.getvalue())
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@convert.command(name="format")
@click.argument("input_file")
@click.option("--output", "-o", help="Output file")
@click.option("--indent", default=2, type=int)
def format_json(input_file, output, indent):
    """Format/pretty-print JSON."""
    try:
        with open(input_file) as f:
            data = json.load(f)
        
        formatted = json.dumps(data, indent=indent, ensure_ascii=False)
        
        if output:
            with open(output, 'w') as f:
                f.write(formatted)
            console.print(f"[success]✓ Saved to {output}[/success]")
        else:
            syntax = Syntax(formatted, "json", theme="monokai")
            console.print(syntax)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@convert.command(name="minify")
@click.argument("input_file")
@click.option("--output", "-o", help="Output file")
def minify_json(input_file, output):
    """Minify JSON."""
    try:
        with open(input_file) as f:
            data = json.load(f)
        
        minified = json.dumps(data, separators=(',', ':'))
        
        if output:
            with open(output, 'w') as f:
                f.write(minified)
            console.print(f"[success]✓ Saved to {output}[/success]")
        else:
            console.print(minified)
        
        original_size = Path(input_file).stat().st_size
        new_size = len(minified)
        savings = ((original_size - new_size) / original_size) * 100
        
        console.print(f"\n[muted]Size: {original_size} → {new_size} bytes ({savings:.1f}% smaller)[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@convert.command(name="validate")
@click.argument("input_file")
def validate_json(input_file):
    """Validate JSON file."""
    try:
        with open(input_file) as f:
            json.load(f)
        
        console.print(f"[success]✓ {input_file} is valid JSON[/success]")
    except json.JSONDecodeError as e:
        console.print(f"[error]✗ Invalid JSON at line {e.lineno}, column {e.colno}[/error]")
        console.print(f"[muted]{e.msg}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = convert

if __name__ == "__main__":
    convert()
