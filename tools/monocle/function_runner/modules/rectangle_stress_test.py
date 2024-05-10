import display
import gc
import time

def create_rectangle(x, y, color=0xFFFFFF):
    """Create a rectangle object with given position and fill color."""
    return display.Rectangle(x, y, x + 10, y + 10, color)

def display_with_memory_report(rectangles):
    """Clear display, show all rectangles, and report memory usage."""
    display.clear()  # Assuming clear method is available, reset display
    display.show(*rectangles)  # Display all rectangles from the list
    print(f"Displaying {len(rectangles)} rectangles")
    print("Allocated memory:", gc.mem_alloc(), "bytes")
    print("Free memory:", gc.mem_free(), "bytes")

def main():
    RECT_WIDTH, RECT_HEIGHT = 10, 10
    MAX_WIDTH, MAX_HEIGHT = 640, 400  # Use correct dimensions for your display
    SPACE_BETWEEN = 5  # Specify spacing between rectangles

    max_cols = (MAX_WIDTH - SPACE_BETWEEN) // (RECT_WIDTH + SPACE_BETWEEN)
    max_rows = (MAX_HEIGHT - SPACE_BETWEEN) // (RECT_HEIGHT + SPACE_BETWEEN)
    
    rectangles = []
    y = SPACE_BETWEEN
    for row in range(max_rows):
        x = SPACE_BETWEEN
        for col in range(max_cols):
            rect = create_rectangle(x, y)
            rectangles.append(rect)
            display_with_memory_report(rectangles)
            gc.collect()  # Explicit garbage collection to manage memory
            time.sleep(0.001)  # Brief delay to visibly note changes on display
            x += RECT_WIDTH + SPACE_BETWEEN
        y += RECT_HEIGHT + SPACE_BETWEEN

if __name__ == "__main__":
    main()
