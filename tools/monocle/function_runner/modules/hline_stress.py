import display
import gc
import time

def create_hline(x, y, width, color=0xFFFFFF):
    """Create an HLine object with given position, width, and color."""
    return display.HLine(x, y, width, color)

def display_with_memory_report(hlines):
    """Clear display, show all HLines, and report memory usage."""
    display.clear()  # Assuming clear method is available, reset display
    display.show(*hlines)  # Display all HLines from the list
    print(f"Displaying {len(hlines)} HLines")
    print("Allocated memory:", gc.mem_alloc(), "bytes")
    print("Free memory:", gc.mem_free(), "bytes")

def main():
    MAX_WIDTH, MAX_HEIGHT = 640, 400  # Use correct dimensions for your display
    ROW_SPACING = 10  # Specify spacing between rows
    HLINE_WIDTH = 9  # Width of each HLine object
    HLINE_SPACING = 1  # Spacing between HLine objects

    max_rows = MAX_HEIGHT // ROW_SPACING
    max_hlines_per_row = MAX_WIDTH // (HLINE_WIDTH + HLINE_SPACING)
    
    hlines = []
    for row in range(max_rows):
        y = row * ROW_SPACING
        
        for i in range(max_hlines_per_row):
            x = i * (HLINE_WIDTH + HLINE_SPACING)
            hline = create_hline(x, y, HLINE_WIDTH)
            hlines.append(hline)
            display_with_memory_report(hlines)
            gc.collect()  # Explicit garbage collection to manage memory
            time.sleep(0.001)  # Brief delay to visibly note changes on display

if __name__ == "__main__":
    main()
