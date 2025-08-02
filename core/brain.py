import asyncio
from llm.generator import generate_response
from core.memory import ShortTermMemory
from core.personality import get_personality
from plugins.plugin_manager import get_enabled_plugins, apply_plugin_hooks, handle_plugin_command

memory = ShortTermMemory()

async def run_conversation_async(use_voice, input_fn, output_fn):
    personality = get_personality()
    while True:
        user_input = input_fn()
        if not user_input.strip():
            continue

        # Intercept plugin commands
        if user_input.startswith("plugin"):
            handle_plugin_command(user_input)
            continue  # Skip response generation

        memory.add("user", user_input)
        context = memory.get_recent(5)
        context = apply_plugin_hooks(context)

        response = generate_response(context, personality)
        memory.add("assistant", response)
        output_fn(response)
