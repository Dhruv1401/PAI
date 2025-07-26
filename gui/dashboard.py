from plugins.plugin_manager import PluginManager

def show_dashboard():
    pm = PluginManager()
    print("=== TARS Plugin Dashboard ===")
    for name, enabled in pm.list_plugins().items():
        print(f"  • {name}: {'ON' if enabled else 'OFF'}")
    print("\nYou can also type commands:");
    print("  plugin list")
    print("  plugin enable <name>")
    print("  plugin disable <name>")
