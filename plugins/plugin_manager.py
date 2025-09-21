import os
import importlib
import json

PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__))
ENABLED_PLUGINS_FILE = os.path.join(PLUGIN_FOLDER, "plugin_config.json")

# Load enabled plugins
def load_enabled_plugins():
    if not os.path.exists(ENABLED_PLUGINS_FILE):
        return {}
    with open(ENABLED_PLUGINS_FILE, "r") as f:
        return json.load(f)

# Save enabled plugins
def save_enabled_plugins(enabled_plugins):
    with open(ENABLED_PLUGINS_FILE, "w") as f:
        json.dump(enabled_plugins, f, indent=2)

# List all plugins
def list_all_plugins():
    return [
        name for name in os.listdir(PLUGIN_FOLDER)
        if os.path.isdir(os.path.join(PLUGIN_FOLDER, name)) or name.endswith(".py")
        and not name.startswith("__")
    ]

# Enable plugin
def enable_plugin(name):
    enabled = load_enabled_plugins()
    if name in enabled and enabled[name]:
        print(f"ℹ️ Plugin '{name}' already enabled.")
        return
    enabled[name] = True
    save_enabled_plugins(enabled)
    print(f"✅ Plugin '{name}' enabled.")

# Disable plugin
def disable_plugin(name):
    enabled = load_enabled_plugins()
    if name not in enabled or not enabled[name]:
        print(f"ℹ️ Plugin '{name}' already disabled.")
        return
    enabled[name] = False
    save_enabled_plugins(enabled)
    print(f"🛑 Plugin '{name}' disabled.")

# Load plugin modules
def get_enabled_plugins():
    enabled = load_enabled_plugins()
    plugins = []
    for name, status in enabled.items():
        if status:
            try:
                module_path = f"plugins.{name}" if not name.endswith(".py") else f"plugins.{name[:-3]}"
                module = importlib.import_module(module_path)
                plugins.append(module)
            except ImportError as e:
                print(f"⚠️ Failed to load plugin '{name}': {e}")
    return plugins

# Apply plugin hooks (returns response if any)
def apply_plugin_hooks(context, user_input):
    plugins = get_enabled_plugins()
    for plugin in plugins:
        if hasattr(plugin, "hook"):
            response = plugin.hook(user_input)
            if response:
                return response
    return None

# Handle plugin commands
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
            print("❌ Unknown command. Use: plugin enable <name> or plugin disable <name>")
    else:
        print("❌ Invalid plugin command. Use: plugin list, plugin enable <name>, plugin disable <name>)")
