import os
import importlib
import json

PLUGIN_FOLDER = "plugins"
PLUGIN_CONFIG_FILE = os.path.join(PLUGIN_FOLDER, "plugin_config.json")

def load_plugins():
    plugins = {}
    for filename in os.listdir(PLUGIN_FOLDER):
        if filename.endswith(".py") and filename != "plugin_manager.py":
            plugin_name = filename[:-3]
            try:
                module = importlib.import_module(f"plugins.{plugin_name}")
                if hasattr(module, "apply"):
                    plugins[plugin_name] = module
            except Exception as e:
                print(f"[PluginManager] Failed to load {plugin_name}: {e}")
    return plugins

def load_plugin_config():
    try:
        with open(PLUGIN_CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_plugin_config(config):
    with open(PLUGIN_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_enabled_plugins():
    config = load_plugin_config()
    return [name for name, status in config.items() if status]

def apply_plugin_hooks(context):
    plugins = load_plugins()
    enabled = get_enabled_plugins()
    for name in enabled:
        plugin = plugins.get(name)
        if plugin and hasattr(plugin, "apply"):
            try:
                context = plugin.apply(context)
            except Exception as e:
                print(f"[PluginManager] Plugin {name} apply() failed: {e}")
    return context

def show_plugin_dashboard():
    config = load_plugin_config()
    print("\n=== TARS Plugin Dashboard ===")
    for name, status in config.items():
        print(f"  • {name}: {'ON' if status else 'OFF'}")
    print("\nYou can also type commands:")
    print("  plugin list")
    print("  plugin enable <name>")
    print("  plugin disable <name>\n")

    # Show running plugins list
    print("🔌 Enabled Plugins:", ", ".join(get_enabled_plugins()))

    return "voice_interface" in get_enabled_plugins()

def handle_plugin_command(command):
    tokens = command.strip().split()
    if len(tokens) < 2:
        print("[PluginManager] Invalid plugin command.")
        return

    config = load_plugin_config()

    action, name = tokens[1], tokens[2] if len(tokens) > 2 else None

    if action == "list":
        print("Available plugins:")
        for filename in os.listdir(PLUGIN_FOLDER):
            if filename.endswith(".py") and filename != "plugin_manager.py":
                print(f"  - {filename[:-3]}")
    elif action == "enable" and name:
        config[name] = True
        # Auto-toggle voice/text interface
        if name == "voice_interface":
            config["text_interface"] = False
        elif name == "text_interface":
            config["voice_interface"] = False
        save_plugin_config(config)
        print(f"✅ Plugin '{name}' enabled.")
    elif action == "disable" and name:
        config[name] = False
        save_plugin_config(config)
        print(f"❌ Plugin '{name}' disabled.")
    else:
        print("[PluginManager] Invalid plugin command.")

# Auto-init debug logger
enabled_plugins = get_enabled_plugins()
if "debug_logger" in enabled_plugins:
    try:
        import plugins.debug_logger.debug_logger as debug_logger
        debug_logger.init()
        print("[PluginManager] Debug logger initialized.")
    except Exception as e:
        print(f"[PluginManager] Failed to initialize debug logger: {e}")
