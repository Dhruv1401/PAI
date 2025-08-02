import os
import importlib
import json

PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__))
ENABLED_PLUGINS_FILE = os.path.join(PLUGIN_FOLDER, "enabled_plugins.json")

# Load enabled plugins from JSON file
def load_enabled_plugins():
    if not os.path.exists(ENABLED_PLUGINS_FILE):
        return []
    with open(ENABLED_PLUGINS_FILE, "r") as f:
        return json.load(f)

# Save enabled plugins to JSON file
def save_enabled_plugins(enabled_plugins):
    with open(ENABLED_PLUGINS_FILE, "w") as f:
        json.dump(enabled_plugins, f, indent=2)

# Get list of all available plugins (by folder name)
def list_all_plugins():
    return [
        name for name in os.listdir(PLUGIN_FOLDER)
        if os.path.isdir(os.path.join(PLUGIN_FOLDER, name))
        and os.path.exists(os.path.join(PLUGIN_FOLDER, name, "plugin.py"))
        and not name.startswith("__")
    ]

# Enable a plugin
def enable_plugin(plugin_name):
    available = list_all_plugins()
    if plugin_name not in available:
        print(f"❌ Plugin '{plugin_name}' does not exist.")
        return

    enabled = load_enabled_plugins()
    if plugin_name not in enabled:
        enabled.append(plugin_name)
        save_enabled_plugins(enabled)
        print(f"✅ Plugin '{plugin_name}' enabled.")
    else:
        print(f"ℹ️ Plugin '{plugin_name}' is already enabled.")

# Disable a plugin
def disable_plugin(plugin_name):
    enabled = load_enabled_plugins()
    if plugin_name not in enabled:
        print(f"❌ Plugin '{plugin_name}' is not enabled.")
        return

    enabled.remove(plugin_name)
    save_enabled_plugins(enabled)
    print(f"🛑 Plugin '{plugin_name}' disabled.")

# Load enabled plugin modules
def get_enabled_plugins():
    enabled = load_enabled_plugins()
    plugins = []
    for name in enabled:
        try:
            module_path = f"plugins.{name}.plugin"
            module = importlib.import_module(module_path)
            plugins.append(module)
        except ImportError:
            print(f"⚠️ Failed to load plugin: {name}")
    return plugins

# Apply plugin hooks (modify context)
def apply_plugin_hooks(context):
    plugins = get_enabled_plugins()
    for plugin in plugins:
        if hasattr(plugin, "hook"):
            context = plugin.hook(context)
    return context

# Handle typed plugin commands
def handle_plugin_command(command):
    tokens = command.strip().split()
    if len(tokens) == 2 and tokens[1] == "list":
        print("Available plugins:")
        for plugin in list_all_plugins():
            print(f"  - {plugin}")
    elif len(tokens) == 3:
        action, name = tokens[1], tokens[2]
        if action == "enable":
            enable_plugin(name)
        elif action == "disable":
            disable_plugin(name)
        else:
            print("❌ Unknown command. Try: plugin enable <name> or plugin disable <name>")
    else:
        print("❌ Invalid plugin command. Use: plugin list, plugin enable <name>, plugin disable <name>")
