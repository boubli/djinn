# System Monitor Plugin

Advanced system monitoring for DJINN - CPU, RAM, Disk, Network.

## Installation

```bash
djinn market install system-monitor
```

## Requirements

- `psutil>=5.9`

## Usage

```bash
# Show CPU usage
djinn monitor cpu

# Show memory usage
djinn monitor memory

# Show disk usage
djinn monitor disk

# Show network stats
djinn monitor network

# Show all information
djinn monitor all
```

## Screenshots

```
🖥️  CPU Information

┏━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Core  ┃ Usage ┃ Bar                    ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Core 0│ 25%   │ █████░░░░░░░░░░░░░░░░░ │
│ Core 1│ 15%   │ ███░░░░░░░░░░░░░░░░░░░ │
└───────┴───────┴────────────────────────┘
```

## Author

DJINN Team

## License

MIT
