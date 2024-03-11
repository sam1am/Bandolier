# main.py
import asyncio
from threading import Thread
from queue import Queue
from brilliant_monocle_driver import Monocle
from note_manager import NoteManager
from input_listener import InputListener
from display_manager import prepare_display_command
from callbacks import callback
from datetime import datetime

async def update_display(mono, text, title):
    display_commands = prepare_display_command(text.split('\n'), title)
    try:
        await mono.send(display_commands)
    except Exception as e:
        print(f"Error in update_display: {e}")

async def main():
    mono = Monocle(callback)
    note_manager = NoteManager('notes.db')

    # Create a queue for inter-thread communication
    display_queue = Queue()

    # Define the function to add updates to the queue
    def queue_update_display(text, title):
        display_queue.put((text, title))

    async with mono:
        await update_display(mono, '>', datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
        current_loop = asyncio.get_running_loop()
        # Initialize the InputListener with the queue and note manager
        # input_listener = InputListener(display_queue, note_manager, current_loop)
        input_listener = InputListener(display_queue, note_manager, current_loop)


        Thread(target=input_listener.start, daemon=True).start()

        while True:
            # Process tasks from the queue
            while not display_queue.empty():
                text, title = display_queue.get()
                await update_display(mono, text, title)
            await asyncio.sleep(1)

    note_manager.close()

if __name__ == "__main__":
    asyncio.run(main())
