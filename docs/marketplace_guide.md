# DJINN Marketplace Guide (Beta)

Welcome to the **DJINN Marketplace**, a decentralized registry for community-created plugins.

## 🛒 Using the Marketplace

### List Available Plugins
Browse the catalog of verified plugins:
```bash
djinn market list
```

### Install a Plugin
Found something you like? Install it with one command:
```bash
djinn market install <plugin_name>
```

**Example:**
```bash
djinn market install system-monitor
```

---

## 📦 How to Publish a Plugin

The marketplace is simply a JSON file hosted on GitHub. To publish your plugin:

1.  **Create your Plugin**: Write a Python script that uses `click` or standard python code.
2.  **Host it**: Upload the `.py` file to a public URL (GitHub Gist, Repo, etc.).
3.  **Register it**:
    *   Fork the [DJINN Repository](https://github.com/boubli/djinn).
    *   Edit `registry.json`.
    *   Add your plugin details:
        ```json
        "my-plugin": {
            "description": "Does amazing things",
            "author": "Your Name",
            "url": "https://raw.githubusercontent.com/you/repo/master/plugin.py",
            "version": "1.0.0"
        }
        ```
    *   Submit a **Pull Request**.

Once merged, your plugin will be instantly available to everyone via `djinn market install`!
