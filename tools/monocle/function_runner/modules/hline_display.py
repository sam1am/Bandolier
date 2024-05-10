import display
import time
import gc
import random

def create_hline(x, y, color):
    """Create and return an HLine object."""
    return display.HLine(x, y, 10, color)

def main():
    MAX_WIDTH, MAX_HEIGHT = 640, 400  # Display dimensions
    HLINE_WIDTH = 10
    NUM_HLINES = 100
    HLINES_PER_ROW = int((MAX_WIDTH / HLINE_WIDTH) ** 0.5)  # Estimate the number of HLines per row for a square grid
    HLINES_PER_COLUMN = NUM_HLINES // HLINES_PER_ROW
    
    x_spacing = MAX_WIDTH // HLINES_PER_ROW
    y_spacing = MAX_HEIGHT // HLINES_PER_COLUMN
    
    # Define a set of 16 random colors (in hexadecimal)
    colors = [
        0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF,
        0xC0C0C0, 0x808080, 0x800000, 0x808000, 0x008000, 0x800080,
        0x008080, 0x000080, 0x000000, 0xFFFFFF
    ]

    hlines = []
    # Generate HLine coordinates
    for row in range(HLINES_PER_COLUMN):
        for col in range(HLINES_PER_ROW):
            if len(hlines) == NUM_HLINES:
                break
            
            x = col * x_spacing + (x_spacing - HLINE_WIDTH) // 2
            y = row * y_spacing
            color = random.choice(colors)  # Select a random color for each HLine
            hline = create_hline(x, y, color)
            hlines.append(hline)
        
        if len(hlines) == NUM_HLINES:
            break
    
    display.clear()  # Assuming a method to clear the display
    display.show(*hlines)  # Display all HLines
    print(f"Displayed {len(hlines)} HLines with random colors")

    gc.collect()  # Collect garbage, if necessary

if __name__ == "__main__":
    main()
