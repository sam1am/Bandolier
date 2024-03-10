import asyncio
from brilliant_monocle_driver import Monocle
from pynput import keyboard
from threading import Thread

DISPLAY_PIXEL_HEIGHT = 400
DISPLAY_PIXEL_WIDTH = 640
MAX_LINE_LENGTH = 26
LINE_HEIGHT = 50
STATUS_LINE_HEIGHT = LINE_HEIGHT  # Height of the status line
HORIZONTAL_LINE_Y = DISPLAY_PIXEL_HEIGHT - (STATUS_LINE_HEIGHT * 2)  # Y-coordinate for the horizontal line
max_lines = (DISPLAY_PIXEL_HEIGHT - STATUS_LINE_HEIGHT * 2) // LINE_HEIGHT  # Adjust for status and horizontal line

def callback(channel, text_in):
    """
    Callback to handle incoming text from the Monocle.
    """
    print(text_in)

def prepare_display_command(lines, max_lines):
    # Initialize the command with the import statement
    command = "import display\n\n"

    # Ensure we do not exceed the display's line capacity
    display_lines = lines[:max_lines]

    display_commands = []
    for idx, line in enumerate(display_lines):
        # Escape single quotes in the line
        line = line.replace("'", "\\'")

        # Split long lines into multiple displayable segments if needed
        segment = ""
        words = line.split(' ')
        for word in words:
            if len(segment) + len(word) + 1 > MAX_LINE_LENGTH:
                line_var = f"line{len(display_commands)+1}"
                line_command = f"{line_var} = display.Text('{segment.strip()}', 0, {idx * LINE_HEIGHT}, 0xFFFFFF)"
                display_commands.append(line_command)
                segment = word + ' '  # Start a new segment
                idx += 1  # Move to the next line
            else:
                segment += word + ' '
        # Add the last segment
        if segment.strip():
            line_var = f"line{len(display_commands)+1}"
            line_command = f"{line_var} = display.Text('{segment.strip()}', 0, {idx * LINE_HEIGHT}, 0xFFFFFF)"
            display_commands.append(line_command)

    # Add the horizontal line and the status indicator
    status_line = f"status_line = display.Text('Typing', 0, {DISPLAY_PIXEL_HEIGHT - STATUS_LINE_HEIGHT}, 0xFFFFFF, justify=display.BOTTOM_LEFT)"
    horizontal_line = f"horizontal_line = display.HLine(0, {HORIZONTAL_LINE_Y}, {DISPLAY_PIXEL_WIDTH}, 0xFFFFFF)"
    
    # Add the lines to the command string
    command += "\n".join(display_commands) + "\n"
    command += status_line + "\n"
    command += horizontal_line + "\n\n"
    
    # Add the display.show() command with the status and horizontal line
    command += f"display.show({', '.join([cmd.split()[0] for cmd in display_commands])}, status_line, horizontal_line)\n"

    return command

async def update_display(mono, text, max_lines):
    """
    Async function to update the display with the given text.
    """
    lines = text.split('\n')  # Split text into lines for display
    display_commands = prepare_display_command(lines, max_lines)
    await mono.send(display_commands)

def listen_for_keypress(mono, loop, max_lines):
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
            asyncio.run_coroutine_threadsafe(update_display(mono, '\n'.join(lines), max_lines), loop)
        except Exception as e:
            print(f"Error: {e}")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()




async def main():
    mono = Monocle(callback)
    loop = asyncio.get_running_loop()
    async with mono:
        # Initialize the display with '>' to indicate readiness
        await update_display(mono, '>', max_lines)

        # Start the thread that listens for keyboard events.
        # Pass max_lines to listen_for_keypress
        Thread(target=listen_for_keypress, args=(mono, loop, max_lines), daemon=True).start()

        # Keep the application running to listen for keypresses.
        while True:
            await asyncio.sleep(1)


# Run the application
asyncio.run(main())