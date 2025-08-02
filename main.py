import asyncio
from interface.text_interface import text_input, text_output
from interface.voice_interface import voice_input, voice_output
from core.brain import run_conversation_async
from plugins.plugin_manager import show_plugin_dashboard, get_enabled_plugins

def main():
    show_plugin_dashboard()
    enabled_plugins = get_enabled_plugins()
    print("\n📦 Active Plugins:", ", ".join(enabled_plugins))

    if "voice_interface" in enabled_plugins:
        asyncio.run(run_conversation_async(True, voice_input, voice_output))
    else:
        asyncio.run(run_conversation_async(False, text_input, text_output))

if __name__ == "__main__":
    main()
