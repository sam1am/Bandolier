import display
import time
import gc
import random

def create_rectangle(x, y, color):
    """Create and return a rectangle object."""
    return display.Rectangle(x, y, x + 10, y + 10, color)

def main():
    MAX_WIDTH, MAX_HEIGHT = 640, 400  # Display dimensions
    RECT_WIDTH, RECT_HEIGHT = 10, 10
    NUM_RECTANGLES = 120
    RECTANGLES_PER_ROW = int((MAX_WIDTH / RECT_WIDTH) ** 0.5)  # Estimate the number of rectangles per row for a square grid
    RECTANGLES_PER_COLUMN = NUM_RECTANGLES // RECTANGLES_PER_ROW
    
    x_spacing = MAX_WIDTH // RECTANGLES_PER_ROW
    y_spacing = MAX_HEIGHT // RECTANGLES_PER_COLUMN
    
    # Define a set of 16 random colors (in hexadecimal)
    colors = [
        0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF,
        0xC0C0C0, 0x808080, 0x800000, 0x808000, 0x008000, 0x800080,
        0x008080, 0x000080, 0x000000, 0xFFFFFF
    ]

    rectangles = []
    # Generate rectangle coordinates
    for row in range(RECTANGLES_PER_COLUMN):
        for col in range(RECTANGLES_PER_ROW):
            if len(rectangles) == NUM_RECTANGLES:
                break
            
            x = col * x_spacing + (x_spacing - RECT_WIDTH) // 2
            y = row * y_spacing + (y_spacing - RECT_HEIGHT) // 2
            color = random.choice(colors)  # Select a random color for each rectangle
            rect = create_rectangle(x, y, color)
            rectangles.append(rect)
        
        if len(rectangles) == NUM_RECTANGLES:
            break
    
    display.clear()  # Assuming a method to clear the display
    display.show(*rectangles)  # Display all rectangles
    print(f"Displayed {len(rectangles)} rectangles with random colors")

    gc.collect()  # Collect garbage, if necessary

if __name__ == "__main__":
    main()
