import asyncio
from interface.text_interface import text_input, text_output
from interface.voice_interface import voice_input, voice_output
from core.brain import run_conversation_async
from plugins.plugin_manager import get_enabled_plugins

def main():
    print("=== Welcome to PAI ===")
    print("Type 'plugin list' to see plugins.\n")

    enabled_plugins = get_enabled_plugins()
    print("=== Active Plugins ===")
    for plugin in enabled_plugins:
        print(f"  - {plugin.__name__}")

    # Main loop
    while True:
        user_input = text_input()
        asyncio.run(run_conversation_async(False, lambda: user_input, text_output))

if __name__ == "__main__":
    main()
