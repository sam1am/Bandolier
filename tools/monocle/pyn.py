from pynput.keyboard import Key, Listener

def on_press(key):
    try:
        # If the key is a standard key, it will not have a special value
        print(f'Alphanumeric key pressed: {key.char}')
    except AttributeError:
        # If it's a special key, it will have a special value
        print(f'Special key pressed: {key}')

def on_release(key):
    # Stop listener
    if key == Key.esc:
        return False

# Set up the listener
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# Note that this script will continue running and displaying keys
# until the escape key is pressed.
