import asyncio
from brilliant_monocle_driver import Monocle
from pynput import keyboard
from threading import Thread

def callback(channel, text_in):
    """
    Callback to handle incoming text from the Monocle.
    """
    print(text_in)

def prepare_display_command(lines):
    MAX_LINE_LENGTH = 26
    LINE_HEIGHT = 50  # Assuming a fixed line height for simplicity

    # Initialize the command with the import statement
    command = "import display\n\n"

    display_commands = []
    for idx, line in enumerate(lines):
        # Split long lines into multiple displayable segments if needed
        for i in range(0, len(line), MAX_LINE_LENGTH):
            segment = line[i:i+MAX_LINE_LENGTH].replace("'", "\\'")  # Escape single quotes in text
            line_var = f"line{len(display_commands)+1}"
            line_command = f"{line_var} = display.Text('{segment}', 0, {idx * LINE_HEIGHT}, 0xFFFFFF)"
            display_commands.append(line_command)

    # Add the lines to the command string
    command += "\n".join(display_commands) + "\n\n"
    # Add the display.show() command
    command += f"display.show({', '.join([cmd.split()[0] for cmd in display_commands])})\n"

    return command

# The rest of your script remains unchanged, including the async main function and the listen_for_keypress function.





# async def execute(text):
#     """
#     Sends the given text to the display, divided into appropriate chunks.
#     """
#     mono = Monocle(callback)
#     async with mono:
#         display_commands = prepare_display_command(text)
#         # Assuming that the `mono.send` method can execute the display.show command with the objects directly.
#         # You might need to adjust this part based on how `mono.send` works.
#         await mono.send(display_commands)


async def update_display(mono, text):
    """
    Async function to update the display with the given text.
    """
    lines = text.split('\n')  # Split text into lines for display
    display_commands = prepare_display_command(lines)
    await mono.send(display_commands)


def listen_for_keypress(mono, loop):
    """
    Listens for keypress events and updates the display accordingly.
    """
    lines = [""]  # Start with a single empty line

    def on_press(key):
        nonlocal lines
        try:
            if hasattr(key, 'char') and key.char:
                # It's a character key, append to the current line
                lines[-1] += key.char
            elif key == keyboard.Key.space:
                # Handle the space key, append space to the current line
                lines[-1] += ' '
            elif key == keyboard.Key.backspace:
                # Handle the backspace key, remove last character of the current line
                if lines[-1]:
                    lines[-1] = lines[-1][:-1]
                elif len(lines) > 1:  # If the current line is empty and not the first line, remove the line
                    lines.pop()
            elif key == keyboard.Key.enter:
                # Handle the enter key, start a new line
                lines.append("")
            else:
                # Ignore other special keys
                return

            # Update display with the current state of lines
            asyncio.run_coroutine_threadsafe(update_display(mono, '\n'.join(lines)), loop)
        except Exception as e:
            print(f"Error: {e}")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()



async def main():
    mono = Monocle(callback)
    loop = asyncio.get_running_loop()
    async with mono:
        # Initialize the display with '>' to indicate readiness
        await update_display(mono, '>')

        # Start the thread that listens for keyboard events.
        Thread(target=listen_for_keypress, args=(mono, loop), daemon=True).start()

        # Keep the application running to listen for keypresses.
        while True:
            await asyncio.sleep(1)

# Run the application
asyncio.run(main())