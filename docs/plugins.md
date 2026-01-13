# Subcommands & Plugins

DJINN supports extending functionality via **Subcommands** (internally called Plugins).

## Using Plugins
Currently, plugins are built-in. You can access them via:
```bash
djinn <plugin_name> [args]
```

## Available Plugins

### `git`
Optimized for Version Control.
`djinn git "undo last commit"`

### `docker`
Optimized for DevOps.
`djinn docker "stop all containers"`

### `theme`
Customize the look of DJINN.
`djinn theme set cyberpunk`

## Developing Plugins (Coming Soon)
We are working on a dynamic plugin system that will allow you to drop python scripts into a `~/.djinn/plugins` folder.

Stay tuned for the **Marketplace** update!
