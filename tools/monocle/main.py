import asyncio
from brilliant_monocle_driver import Monocle

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



async def execute(text):
    """
    Sends the given text to the display, divided into appropriate chunks.
    """
    mono = Monocle(callback)
    async with mono:
        display_commands = prepare_display_command(text)
        # Assuming that the `mono.send` method can execute the display.show command with the objects directly.
        # You might need to adjust this part based on how `mono.send` works.
        await mono.send(display_commands)


# Example usage
text = "Your long text message that is very long and needs to be put on multiple lines."
asyncio.run(execute(text))
