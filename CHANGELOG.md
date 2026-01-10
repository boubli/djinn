# Changelog

All notable changes to DJINN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-01-10

### Added
- 🎉 Initial release of DJINN
- 87 specialized commands across 14 categories
- Multi-LLM backend support (Ollama, LM Studio, OpenAI)
- 5 color themes (default, hacker, ocean, purple, minimal)
- Template system with 6 built-in templates
- Snippet system for saving multi-line commands
- Alias system for shortcuts
- Danger detection for destructive commands
- Dry-run mode to preview command effects
- AI chat mode for interactive conversations
- Shell translation between bash/powershell/zsh
- Code generation in any language
- Commit message generation
- README and changelog generation
- Fuzzy search through history

### Commands by Category
- **Core**: djinn, explain, undo, suggest, check, dryrun
- **DevOps**: git, docker, k8s, terraform, helm, ansible, vagrant
- **Cloud**: aws, gcp, azure, ssh, api
- **Databases**: mysql, postgres, redis, mongo, sql, graphql
- **Languages**: python, node, rust, go, java, cpp
- **AI**: chat, translate, codegen, script, oneliner
- **Productivity**: commit, changelog, readme, docs, todo
- **Security**: firewall, ssl, network, nmap, gpg
- **Mobile**: react, flutter, android, ios
- **Data/ML**: pandas, spark, jupyter
- And many more...

### Technical
- Click-based CLI architecture
- Modular plugin system
- Rich terminal UI with spinners
- Clipboard integration
- SQLite history storage
- JSON configuration
