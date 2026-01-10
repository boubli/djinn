# DJINN Documentation

Welcome to the official documentation for **DJINN** - Terminal Sorcery at Your Command.

## What is DJINN?

DJINN is an AI-powered CLI tool that converts natural language to shell commands. With **87 specialized commands**, it covers everything from Git to Kubernetes, from FFmpeg to SQL queries.

## Quick Navigation

- [Installation](installation.md)
- [Configuration](configuration.md)
- [Commands](commands.md)
- [Themes](themes.md)
- [API Reference](api.md)

## Features

- 🤖 **AI-Powered**: Understands natural language
- ⚡ **87 Commands**: Specialized plugins for every tool
- 🔄 **Multi-LLM Support**: Ollama, LM Studio, OpenAI
- 📋 **Auto-Copy**: Commands ready to paste
- 🎨 **5 Themes**: Customize your experience
- 🔒 **Danger Detection**: Safety first

## Example

```bash
# Ask in natural language
djinn "find all Python files modified today"

# Get the command
✓ find . -name "*.py" -mtime 0

# Execute directly
djinn -x "delete temp files"
```

## Getting Started

```bash
pip install djinn-cli
djinn "hello world"
```
