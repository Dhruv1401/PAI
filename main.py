import asyncio
from interface.text_interface import text_input, text_output
from core.brain import run_conversation_async
from plugins.plugin_manager import show_plugin_dashboard

def main():
    use_voice = show_plugin_dashboard()  # Now controlled from dashboard
    asyncio.run(run_conversation_async(use_voice, text_input, text_output))

if __name__ == "__main__":
    main()
    