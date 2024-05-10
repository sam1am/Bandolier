import asyncio
from brilliant_monocle_driver import Monocle

COMMAND = """
import display
import gc

def test_max_characters_per_row():
    row = ""
    while True:
        text_obj = display.Text(row + "A", 0, 0, display.WHITE)
        display.show(text_obj)
        if text_obj.width() > display.WIDTH:
            break
        row += "A"
    return len(row)

def test_max_rows():
    rows = []
    while True:
        try:
            row = "A" * 20  # Adjust the number of characters per row as needed
            text_obj = display.Text(row, 0, len(rows) * display.FONT_HEIGHT, display.WHITE)
            display.show(text_obj)
            rows.append(row)
        except MemoryError:
            break
    return len(rows)

max_chars_per_row = test_max_characters_per_row()
max_rows = test_max_rows()

print("Max characters per row:", max_chars_per_row)
print("Max rows:", max_rows)

display.clear()
gc.collect()
"""

def callback(channel, text_in):
    print(text_in)

async def execute():
    mono = Monocle(callback)
    async with mono:
        await mono.send(COMMAND)

asyncio.run(execute())
