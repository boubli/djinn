# Configuration

## Setting the Backend

DJINN supports multiple LLM backends:

```bash
# Ollama (recommended, free, local)
djinn config --backend ollama
djinn config --model llama3

# LM Studio (local)
djinn config --backend lmstudio

# OpenAI (cloud, requires API key)
export OPENAI_API_KEY="your-key"
djinn config --backend openai
djinn config --model gpt-4
```

## View Current Config

```bash
djinn config --show
```

## Config File Location

Config is stored at: `~/.djinn/config.json`

```json
{
  "backend": "ollama",
  "model": "llama3",
  "context_enabled": true,
  "auto_copy": true,
  "confirm_execute": true,
  "theme": "default"
}
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `backend` | LLM provider | `ollama` |
| `model` | Model name | `null` (auto) |
| `context_enabled` | Include directory context | `true` |
| `auto_copy` | Copy to clipboard | `true` |
| `confirm_execute` | Ask before running | `true` |
| `theme` | Color theme | `default` |

## Themes

```bash
djinn theme default    # Green terminal
djinn theme hacker     # Matrix green
djinn theme ocean      # Blue tones
djinn theme purple     # Purple gradient
djinn theme minimal    # Clean white
```
