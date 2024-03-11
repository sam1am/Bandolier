# display_manager.py
from constants import *

def prepare_display_command(lines, title):
    command = "import display\n\n"
    display_lines = lines[:MAX_LINES]

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
                segment = word + ' '
                idx += 1
            else:
                segment += word + ' '
        if segment.strip():
            line_var = f"line{len(display_commands)+1}"
            line_command = f"{line_var} = display.Text('{segment.strip()}', 0, {idx * LINE_HEIGHT}, 0xFFFFFF)"
            display_commands.append(line_command)
            cursor_x_position = len(segment.strip()) * (DISPLAY_PIXEL_WIDTH // MAX_LINE_LENGTH)
            cursor_y_position = idx * LINE_HEIGHT + LINE_HEIGHT - 5

    if lines[-1] == "":
        cursor_x_position = 0
        cursor_y_position += LINE_HEIGHT

    status_line = f"status_line = display.Text('{title}', 0, {DISPLAY_PIXEL_HEIGHT - STATUS_LINE_HEIGHT}, 0xFFFFFF, justify=display.BOTTOM_LEFT)"
    horizontal_line = f"horizontal_line = display.HLine(0, {HORIZONTAL_LINE_Y}, {DISPLAY_PIXEL_WIDTH}, 0xFFFFFF)"
    
    command += "\n".join(display_commands) + "\n"
    command += status_line + "\n"
    command += horizontal_line + "\n\n"
    
    cursor_line = f"cursor = display.Line({cursor_x_position}, {cursor_y_position}, {cursor_x_position + 10}, {cursor_y_position}, 0xFFFF00, thickness=2)"
    command += cursor_line + "\n\n"
    command += f"display.show({', '.join([cmd.split()[0] for cmd in display_commands])}, status_line, horizontal_line, cursor)\n"

    return command
