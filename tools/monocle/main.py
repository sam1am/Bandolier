import asyncio
from brilliant_monocle_driver import Monocle
from pynput import keyboard
from threading import Thread

def callback(channel, text_in):
    """
    Callback to handle incoming text from the Monocle.
    """
    print(text_in)

def prepare_display_command(text):
    MAX_LENGTH = 288
    MAX_LINE_LENGTH = 26

    if len(text) > MAX_LENGTH:
        raise ValueError("Text exceeds the maximum allowed length of 288 characters.")

    # Initialize the command with the import statement
    command = "import display\n\n"

    lines = []
    display_objects = []
    for j, i in enumerate(range(0, len(text), MAX_LINE_LENGTH)):
        line_var = f"line{j+1}"
        line_text = text[i:i+MAX_LINE_LENGTH].replace("'", "\\'")  # Escape single quotes in text
        line_command = f"{line_var} = display.Text('{line_text}', 0, {j*50}, 0xFFFFFF)"
        lines.append(line_command)
        display_objects.append(line_var)

    # Add the lines to the command string
    command += "\n".join(lines) + "\n\n"
    # Add the display.show() command
    command += f"display.show({', '.join(display_objects)})\n"

    return command



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
    display_commands = prepare_display_command(text)
    await mono.send(display_commands)

def listen_for_keypress(mono, loop):
    """
    Listens for keypress events and updates the display accordingly.
    """
    text = []

    def on_press(key):
        nonlocal text
        try:
            char = None
            if hasattr(key, 'char') and key.char is not None:
                # It's a character key
                char = key.char
            elif key == keyboard.Key.space:
                # Handle the space key
                text.append(' ')
            elif key == keyboard.Key.backspace:
                # Handle the backspace key
                text = text[:-1]
                asyncio.run_coroutine_threadsafe(update_display(mono, ''.join(text)), loop)
                return
            elif key == keyboard.Key.enter:
                # Handle the enter key
                asyncio.run_coroutine_threadsafe(update_display(mono, ''.join(text)), loop)
                text = []
                return
        
            else:
                # For simplicity, other special keys are ignored in this example
                return
            
            if char:
                text.append(char)  # Add the character to the text
                asyncio.run_coroutine_threadsafe(update_display(mono, ''.join(text)), loop)
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