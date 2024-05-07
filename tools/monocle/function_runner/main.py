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
    selected_module = await asyncio.to_thread(Prompt.select, "Select a module to run (or 'exit' to quit):", module_files + ["exit"])
    return selected_module

async def execute(mono):
    while True:
        # Clear the display
        os.system('clear' if os.name == 'posix' else 'cls')

        # Look for .py files in the ./modules folder
        module_files = [file for file in os.listdir("./modules") if file.endswith(".py")]

        # Use ItsPrompt to select a function to run in a separate thread
        selected_module = await run_prompt(module_files)

        if selected_module == "exit":
            break

        # Read the contents of the selected module file
        with open(f"./modules/{selected_module}", "r") as file:
            module_command = file.read()

        # Send the selected module command to the Monocle
        await mono.send(module_command)

        # Wait for a short duration to allow the script to finish executing
        await asyncio.sleep(1)  # Adjust the delay as needed

async def main():
    print("Looking for monocle...")
    mono = Monocle(callback)
    async with mono:
        # Clear the display
        os.system('clear' if os.name == 'posix' else 'cls')
        await execute(mono)

asyncio.run(main())
