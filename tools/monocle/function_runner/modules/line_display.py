import display
import gc
import time
import random

def create_line(x1, y1, x2, y2, color=0xFFFFFF):
    """Create and return a line object."""
    return display.Line(x1, y1, x2, y2, color)

def display_with_memory_report(lines):
    """Clear display, show all lines, and report memory usage."""
    display.clear()  # Assuming the clear method is available to reset the display
    display.show(*lines)  # Display all lines
    print(f"Displaying {len(lines)} lines")
    print("Allocated memory:", gc.mem_alloc(), "bytes")
    print("Free memory:", gc.mem_free(), "bytes")

def main():
    LINE_LENGTH = 50  # Set line length
    MAX_WIDTH, MAX_HEIGHT = 640, 400  # Display dimensions
    SPACE_BETWEEN = 10  # Specify spacing between lines

    max_lines_per_row = (MAX_WIDTH - SPACE_BETWEEN) // (LINE_LENGTH + SPACE_BETWEEN)
    max_rows = (MAX_HEIGHT - SPACE_BETWEEN) // (SPACE_BETWEEN)
    
    lines = []
    y = SPACE_BETWEEN
    colors = [
        0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF,
        0xC0C0C0, 0x808080, 0x800000, 0x808000, 0x008000, 0x800080,
        0x008080, 0x000080, 0x000000, 0xFFFFFF
    ]
    for row in range(max_rows):
        x1 = SPACE_BETWEEN
        for col in range(max_lines_per_row):
            x2 = x1 + LINE_LENGTH
            color = random.choice(colors)  # Random color for each line
            line = create_line(x1, y, x2, y, color)
            lines.append(line)
            display_with_memory_report(lines)
            gc.collect()  # Explicit garbage collection to manage memory
            time.sleep(0.001)  # Very brief delay to visibly note changes on display
            x1 += LINE_LENGTH + SPACE_BETWEEN
        y += SPACE_BETWEEN
        
if __name__ == "__main__":
    main()
