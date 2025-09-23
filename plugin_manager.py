import importlib

class PluginManager:
    def __init__(self, config, brain):
        self.config = config
        self.brain = brain
        self.plugins = {}

    def load_plugins(self):
        for plugin_name in self.config["enabled_plugins"]:
            try:
                module = importlib.import_module(f"plugins.{plugin_name}")
                self.plugins[plugin_name] = module.Plugin(self.brain, self.config)
                print(f"[PluginManager] Loaded {plugin_name}")
            except Exception as e:
                print(f"[PluginManager] Failed to load {plugin_name}: {e}")

        if hasattr(self.plugins[plugin_name], "log"):
            self.plugins[plugin_name].log(f"{plugin_name} loaded successfully")


    def run(self):
        for plugin in self.plugins.values():
            if hasattr(plugin, "run"):
                plugin.run()


