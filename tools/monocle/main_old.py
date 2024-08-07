import asyncio
from brilliant_monocle_driver import Monocle
from pynput import keyboard
from threading import Thread
import sqlite3
from datetime import datetime
import time

DISPLAY_PIXEL_HEIGHT = 400
DISPLAY_PIXEL_WIDTH = 640
MAX_LINE_LENGTH = 26
LINE_HEIGHT = 50
STATUS_LINE_HEIGHT = LINE_HEIGHT
HORIZONTAL_LINE_Y = DISPLAY_PIXEL_HEIGHT - (STATUS_LINE_HEIGHT * 2)
max_lines = (DISPLAY_PIXEL_HEIGHT - STATUS_LINE_HEIGHT * 2) // LINE_HEIGHT
update_delay = 0.5  # Delay in seconds to wait before batching and sending updates

def callback(channel, text_in):
    print(text_in)

def prepare_display_command(lines, max_lines, title):
    command = "import display\n\n"
    display_lines = lines[:max_lines]
    display_commands = []
    cursor_x_position = 0
    cursor_y_position = 0

    for idx, line in enumerate(display_lines):
        line = line.replace("'", "\\'")
        segment = ""
        words = line.split(' ')
        for word in words:
            if len(segment) + len(word) + 1 > MAX_LINE_LENGTH:
                line_var = f"line{len(display_commands)+1}"
                line_command = f"{line_var} = display.Text('{segment.strip()}', 0, {idx * LINE_HEIGHT}, 0xFFFFFF)"
                display_commands.append(line_command)
                segment = word + ' '  # Start a new segment
                idx += 1
            else:
                segment += word + ' '
        # Add the last segment
        if segment.strip():
            line_var = f"line{len(display_commands)+1}"
            line_command = f"{line_var} = display.Text('{segment.strip()}', 0, {idx * LINE_HEIGHT}, 0xFFFFFF)"
            display_commands.append(line_command)
            cursor_x_position = len(segment.strip()) * (DISPLAY_PIXEL_WIDTH // MAX_LINE_LENGTH)
            cursor_y_position = idx * LINE_HEIGHT + LINE_HEIGHT - 5

    status_line = f"status_line = display.Text('{title}', 0, {DISPLAY_PIXEL_HEIGHT - STATUS_LINE_HEIGHT}, 0xFFFFFF, justify=display.BOTTOM_LEFT)"
    horizontal_line = f"horizontal_line = display.HLine(0, {HORIZONTAL_LINE_Y}, {DISPLAY_PIXEL_WIDTH}, 0xFFFFFF)"

    command += "\n".join(display_commands) + "\n"
    command += status_line + "\n"
    command += horizontal_line + "\n\n"

    cursor_line = f"cursor = display.Line({cursor_x_position}, {cursor_y_position}, {cursor_x_position + 10}, {cursor_y_position}, 0xFFFF00, thickness=2)"
    command += cursor_line + "\n\n"
    command += f"display.show({', '.join([cmd.split()[0] for cmd in display_commands])}, status_line, horizontal_line, cursor)\n"

    return command

async def update_display(mono, text, max_lines, title):
    display_commands = prepare_display_command(text.split('\n'), max_lines, title)
    try:
        await mono.send(display_commands)
    except Exception as e:
        print(f"Error in update_display: {e}")

def listen_for_keypress(mono, loop, max_lines, conn):
    lines = [">"]
    title = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    last_update_request_time = time.time()
    current_note_id = None
    batched_lines = []
    batched_title = title

    def request_update():
        nonlocal last_update_request_time, batched_lines, batched_title
        now = time.time()
        if now - last_update_request_time >= update_delay:
            asyncio.run_coroutine_threadsafe(update_display(mono, '\n'.join(batched_lines), max_lines, batched_title), loop)
            last_update_request_time = now
            batched_lines = lines.copy()
            batched_title = title
        else:
            loop.call_later(0.1, request_update)


    def fetch_note(direction):
        nonlocal current_note_id, lines, title
        with conn:
            c = conn.cursor()
            if current_note_id is None:
                c.execute("SELECT id, title, content FROM notes ORDER BY id DESC LIMIT 1")
            else:
                if direction == 'previous':
                    c.execute("SELECT id, title, content FROM notes WHERE id < ? ORDER BY id DESC LIMIT 1", (current_note_id,))
                else:  # direction == 'next'
                    c.execute("SELECT id, title, content FROM notes WHERE id > ? ORDER BY id ASC LIMIT 1", (current_note_id,))
            note = c.fetchone()
            if note:
                current_note_id, title, content = note
                lines = content.split('\n') + [""]
            elif direction == 'previous':  # No previous note found, do nothing
                pass
            else:  # direction == 'next' and no next note found, create a new note
                current_note_id = None
                title = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                lines = [">"]
            request_update()

    def on_press(key):
        nonlocal lines, title, current_note_id, batched_lines, batched_title
        modified = False
        try:
            if hasattr(key, 'char') and key.char:
                lines[-1] += key.char
                modified = True
            elif key == keyboard.Key.space:
                lines[-1] += ' '
                modified = True
            elif key == keyboard.Key.backspace:
                if lines[-1]:
                    lines[-1] = lines[-1][:-1]
                    modified = True
                elif len(lines) > 1:
                    lines.pop()
                    modified = True
            elif key == keyboard.Key.enter:
                if len(lines) > 1 and not lines[-1]:  # Two consecutive enters pressed
                    if lines[0] != ">":  # Check if the first line is not empty
                        note_content = '\n'.join(lines[:-1])  # Exclude the last empty line
                        with conn:
                            c = conn.cursor()
                            if current_note_id is None:  # If it's a new note
                                c.execute("INSERT INTO notes (timestamp, title, content) VALUES (?, ?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title, note_content))
                                conn.commit()
                            else:  # If it's an existing note being edited
                                c.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, note_content, current_note_id))
                                conn.commit()
                    lines = [">"]  # Reset the lines to a new note
                    title = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")  # Update the title with the current date and time
                    current_note_id = None  # Reset current_note_id to indicate a new note
                    modified = True
                else:
                    lines.append("")  # Start a new line
                    modified = True
            elif key == keyboard.Key.left:
                fetch_note('previous')
            elif key == keyboard.Key.right:
                fetch_note('next')

            if modified:
                batched_lines = lines.copy()
                batched_title = title
                request_update()


        except Exception as e:
            print(f"Error: {e}")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

async def main():
    mono = Monocle(callback)
    loop = asyncio.get_running_loop()

    conn = sqlite3.connect('notes.db', check_same_thread=False)
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS notes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, title TEXT, content TEXT)''')

    async with mono:
        await update_display(mono, '>', max_lines, datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))

        Thread(target=listen_for_keypress, args=(mono, loop, max_lines, conn), daemon=True).start()

        while True:
            await asyncio.sleep(1)

    conn.close()

if __name__ == "__main__":
    asyncio.run(main())
