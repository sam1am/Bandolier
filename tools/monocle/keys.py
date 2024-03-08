import asyncio
import threading
from pynput.keyboard import Key, Listener
from brilliant_monocle_driver import Monocle
import aiohttp

# Initialize the global variables
captured_keystrokes = ""
loop = asyncio.get_event_loop()
mono = Monocle()
command_queue = asyncio.Queue()

async def send_to_display(mono, message):
    UPDATE_DISPLAY_COMMAND = f"""
import display

def show_message(message):
    text_display = display.Text(message, 0, 0, display.WHITE)
    display.show(text_display)

show_message("{message}")
"""
    await mono.send(UPDATE_DISPLAY_COMMAND)

async def process_command():
    global captured_keystrokes
    command = captured_keystrokes.strip()
    if not command:
        return
    url = f"https://roast.wayr.app/infer/?prompt={command}&model=mistral"
    headers = {'accept': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data='') as response:
            if response.status == 200:
                data = await response.json()
                response_text = data.get('response', 'No response')
                print(response_text)
                await send_to_display(mono, response_text)
            else:
                await send_to_display(mono, f"Error: Unable to fetch response, status code: {response.status}")
    captured_keystrokes = ""
    await send_prompt_to_display()

async def process_commands_from_queue():
    while True:
        await command_queue.get()
        await process_command()

async def send_prompt_to_display():
    await send_to_display(mono, ">")

def on_press(key):
    global captured_keystrokes
    try:
        captured_keystrokes += key.char
    except AttributeError:
        if key == Key.enter:
            asyncio.run_coroutine_threadsafe(command_queue.put('process_command'), loop)
        elif key == Key.space:
            captured_keystrokes += ' '
        elif key == Key.backspace and captured_keystrokes:
            captured_keystrokes = captured_keystrokes[:-1]

def on_release(key):
    if key == Key.esc:
        loop.call_soon_threadsafe(loop.stop)
        return False

def start_keyboard_listener():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

async def capture_and_display_keystrokes():
    global captured_keystrokes
    previous_keystrokes = ""
    while True:
        if captured_keystrokes != previous_keystrokes:
            await send_to_display(mono, f">{captured_keystrokes}")
            previous_keystrokes = captured_keystrokes
        await asyncio.sleep(0.1)

async def execute():
    async with mono:
        await send_prompt_to_display()
        listener_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
        listener_thread.start()
        asyncio.create_task(process_commands_from_queue())
        await capture_and_display_keystrokes()

if __name__ == '__main__':
    loop.run_until_complete(execute())
