import json
from plugin_manager import PluginManager
from brain import Brain

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def main():
    config = load_config()
    brain = Brain(config)
    manager = PluginManager(config, brain)

    print("[Jarvis] Starting with plugins:", config["enabled_plugins"])
    manager.load_plugins()

    # GUI or Voice decides how input comes in
    manager.run()

if __name__ == "__main__":
    main()
