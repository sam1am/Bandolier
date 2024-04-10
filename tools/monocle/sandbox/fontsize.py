import asyncio
from brilliant_monocle_driver import Monocle

async def display_text_cycle():
    command_template = """
import display

# Display clear
display.clear()

# Display text simulating font size {size}
text = display.Text('Size {size}x', 1, 1, {color}, justify=display.TOP_LEFT)
display.show(text)
"""

    colors = ['display.RED', 'display.GREEN', 'display.BLUE', 'display.WHITE']
    sizes = range(1, 5)

    mono = Monocle()
    async with mono:
        for i, size in enumerate(sizes):
            command = command_template.format(size=size, color=colors[i % len(colors)])
            await mono.send(command)
            await asyncio.sleep(1)  # Show each "size" for 1 second

asyncio.run(display_text_cycle())
