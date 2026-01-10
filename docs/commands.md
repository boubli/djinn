# All Commands Reference

DJINN has **87 specialized commands** across 14 categories.

---

## Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `djinn "..."` | General command | `djinn "list files"` |
| `djinn -x "..."` | Execute directly | `djinn -x "delete temp"` |
| `djinn -i` | Interactive mode | `djinn -i` |
| `djinn explain "cmd"` | Explain command | `djinn explain "rm -rf"` |
| `djinn undo "cmd"` | Reverse command | `djinn undo "mkdir foo"` |
| `djinn suggest "..."` | Multiple options | `djinn suggest "backup"` |
| `djinn check "cmd"` | Danger detection | `djinn check "rm -rf /"` |
| `djinn dryrun "cmd"` | Preview effects | `djinn dryrun "format disk"` |

---

## DevOps

| Command | Example |
|---------|---------|
| `djinn git "..."` | `djinn git "undo last commit"` |
| `djinn docker "..."` | `djinn docker "stop all containers"` |
| `djinn k8s "..."` | `djinn k8s "list pods"` |
| `djinn terraform "..."` | `djinn terraform "init"` |
| `djinn helm "..."` | `djinn helm "install nginx"` |
| `djinn ansible "..."` | `djinn ansible "ping hosts"` |
| `djinn vagrant "..."` | `djinn vagrant "up"` |

---

## Cloud

| Command | Example |
|---------|---------|
| `djinn aws "..."` | `djinn aws "list s3 buckets"` |
| `djinn gcp "..."` | `djinn gcp "list instances"` |
| `djinn azure "..."` | `djinn azure "list vms"` |
| `djinn ssh user@host "..."` | `djinn ssh root@server "check disk"` |
| `djinn api "..."` | `djinn api "get weather"` |

---

## Databases

| Command | Example |
|---------|---------|
| `djinn mysql "..."` | `djinn mysql "show databases"` |
| `djinn postgres "..."` | `djinn postgres "backup db"` |
| `djinn redis "..."` | `djinn redis "get all keys"` |
| `djinn mongo "..."` | `djinn mongo "find all"` |
| `djinn sql "..."` | `djinn sql "select users over 30"` |
| `djinn graphql "..."` | `djinn graphql "get user by id"` |

---

## Languages

| Command | Example |
|---------|---------|
| `djinn python "..."` | `djinn python "create venv"` |
| `djinn node "..."` | `djinn node "run server"` |
| `djinn rust "..."` | `djinn rust "build release"` |
| `djinn go "..."` | `djinn go "run main"` |
| `djinn java "..."` | `djinn java "maven build"` |
| `djinn cpp "..."` | `djinn cpp "compile with debug"` |

---

## AI Utilities

| Command | Example |
|---------|---------|
| `djinn chat` | Start AI conversation |
| `djinn translate "cmd" --to shell` | `djinn translate "ls -la" --to powershell` |
| `djinn codegen "..." --lang py` | `djinn codegen "factorial" --lang python` |
| `djinn script "..."` | `djinn script "backup and zip"` |
| `djinn oneliner "..."` | `djinn oneliner "count lines"` |

---

## Productivity

| Command | Example |
|---------|---------|
| `djinn commit "..."` | `djinn commit "added login"` |
| `djinn changelog "..."` | `djinn changelog "new feature"` |
| `djinn readme "..."` | `djinn readme "installation section"` |
| `djinn docs "..."` | `djinn docs "function docstring"` |
| `djinn todo "..."` | `djinn todo "add validation"` |

---

## Templates & Aliases

```bash
# Templates
djinn template list                      # View all
djinn template run python-project myapp  # Use template

# Snippets
djinn snippet add deploy "npm build && scp"
djinn snippet run deploy

# Aliases
djinn alias add cleanup "rm -rf node_modules"
djinn @cleanup                           # Use alias
```
