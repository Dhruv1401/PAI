import asyncio
from llm.generator import generate_response
from core.memory import ShortTermMemory
from core.personality import get_personality
from plugins.plugin_manager import apply_plugin_hooks, handle_plugin_command

memory = ShortTermMemory()

async def run_conversation_async(use_voice, input_fn, output_fn):
    personality = get_personality()
    while True:
        user_input = input_fn()
        if not user_input.strip():
            continue

        # Plugin commands
        if user_input.startswith("plugin"):
            handle_plugin_command(user_input)
            continue

        # Check plugins first
        plugin_response = apply_plugin_hooks([], user_input)
        if plugin_response:
            output_fn(plugin_response)
            continue

        memory.add("user", user_input)
        context = memory.get_recent(5)

        response = generate_response(context, personality)
        memory.add("assistant", response)
        output_fn(response)
