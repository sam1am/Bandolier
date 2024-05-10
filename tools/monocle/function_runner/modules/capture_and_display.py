import camera
import display
import bluetooth

# Configuration variables
downsample_factor = 64  # Adjust this value to change the downsampling factor
crop_width = 80  # Adjust this value to change the cropped image width
crop_height = 50  # Adjust this value to change the cropped image height
block_size = 8  # Adjust this value to change the size of each pixel block
chunk_size = 31  # Adjust this value to change the number of pixels processed per chunk (max 31)

# Capture an image
camera.capture()

# Display the heavily pixelated, downsampled, cropped, and color-reduced image in chunks
x, y = 0, 0
while True:
    # Read a chunk of image data
    image_data = camera.read(2 * downsample_factor * chunk_size)
    if not image_data:
        break

    # Process and display the chunk
    for i in range(0, len(image_data), 2 * downsample_factor):
        color = int.from_bytes(image_data[i:i+2], "big")
        if color >= 32768:  # Reduce color palette to black and white only
            color = display.WHITE
        else:
            color = display.BLACK

        if x < crop_width and y < crop_height:
            display.Rectangle(x * block_size, y * block_size, (x + 1) * block_size - 1, (y + 1) * block_size - 1, color)

        x += 1
        if x >= crop_width // block_size:
            x = 0
            y += 1
            if y >= crop_height // block_size:
                break

    # Clear the image data buffer
    image_data = None

display.show()
