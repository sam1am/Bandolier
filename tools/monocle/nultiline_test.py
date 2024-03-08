import asyncio
from brilliant_monocle_driver import Monocle

def callback(channel, text_in):
    """
    Callback to handle incoming text from the Monocle.
    """
    print(text_in)

async def send_test_script():
    """
    Sends a hardcoded MicroPython script to the device.
    """
    test_script = """
import display

line1 = display.Text('This is a test message to be displayed', 0, 0, 0xFFFFFF)
line2 = display.Text(' on the device screen across multiple l', 0, 50, 0xFFFFFF)
line3 = display.Text('ines.', 0, 100, 0xFFFFFF)

display.show(line1, line2, line3)
"""

    mono = Monocle(callback)
    async with mono:
        await mono.send(test_script)

# Execute the test script sending
asyncio.run(send_test_script())
