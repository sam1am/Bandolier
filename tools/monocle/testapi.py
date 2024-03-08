import touch
import display

def display_message(message, line_width=26, line_height=10):
    """
    Displays a message on the screen, splitting it into multiple lines if necessary.
    
    :param message: The message to be displayed.
    :param line_width: Maximum number of characters per line.
    :param line_height: Vertical spacing between lines.
    """
    lines = [message[i:i+line_width] for i in range(0, len(message), line_width)]
    display.clear()  # Clear previous messages
    for index, line in enumerate(lines):
        line_text = display.Text(line, 0, index * line_height, display.WHITE)
        display.show(line_text)

def change_text(button):
    """
    Callback function to change the text on the display when a button is touched.
    
    :param button: The button that was touched.
    """
    new_message = f"Button {button} touched!"
    display_message(new_message)

# Initialize the touch callback
touch.callback(touch.EITHER, change_text)

# Display an initial message
initial_message = "Tap a touch button"
display_message(initial_message)
