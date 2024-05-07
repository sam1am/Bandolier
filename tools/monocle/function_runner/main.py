import asyncio
import os
from brilliant_monocle_driver import Monocle
from ItsPrompt.prompt import Prompt

def callback(channel, text_in):
    """
    Callback to handle incoming text from the Monocle.
    """
    print(text_in)

async def run_prompt(module_files):
    selected_module = await asyncio.to_thread(Prompt.select, "Select a module to run:", module_files)
    return selected_module

async def execute():
    mono = Monocle(callback)
    async with mono:
        # Look for .py files in the ./modules folder
        module_files = [file for file in os.listdir("./modules") if file.endswith(".py")]

        # Use ItsPrompt to select a function to run in a separate thread
        selected_module = await run_prompt(module_files)

        # Read the contents of the selected module file
        with open(f"./modules/{selected_module}", "r") as file:
            module_command = file.read()

        # Send the selected module command to the Monocle
        await mono.send(module_command)

async def main():
    await execute()

asyncio.run(main())