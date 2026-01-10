# Installation

## Requirements

- Python 3.8+
- One of:
  - [Ollama](https://ollama.ai) (recommended, free, local)
  - [LM Studio](https://lmstudio.ai) (local)
  - OpenAI API key

## Install from Source

```bash
# Clone repository
git clone https://github.com/yourusername/djinn.git
cd djinn

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install
pip install -e .

# Verify
djinn --version
```

## Install from PyPI

```bash
pip install djinn-cli
```

## Setup LLM Backend

### Ollama (Recommended)

```bash
# Install Ollama
# Visit https://ollama.ai

# Pull a model
ollama pull llama3

# Configure DJINN
djinn config --backend ollama --model llama3
```

### LM Studio

```bash
# Start LM Studio server on port 1234
# Then configure:
djinn config --backend lmstudio
```

### OpenAI

```bash
# Set API key
export OPENAI_API_KEY="your-key"

# Configure
djinn config --backend openai --model gpt-4
```

## Verify Installation

```bash
# Test a command
djinn "hello world"

# Should output something like:
✓ echo "Hello, World!"
```

## Troubleshooting

### Command not found

```bash
# Add to PATH
pip install --user -e .
# or
python -m djinn.cli "your command"
```

### Ollama not responding

```bash
# Make sure Ollama is running
ollama serve
```
