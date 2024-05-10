import io
from PIL import Image
import asyncio
from brilliant_monocle_driver import Monocle

# Variables to control image compression and resizing
RESIZE_FACTOR = 4  # Resize the image by dividing its dimensions by this factor
JPEG_QUALITY = 50  # JPEG compression quality (1-100, lower value means higher compression)

def prepare_image_payload(image_path):
    # Open the image file
    with Image.open(image_path) as image:
        # Get the original image dimensions
        width, height = image.size

        # Calculate the new dimensions based on the resize factor
        new_width = width // RESIZE_FACTOR
        new_height = height // RESIZE_FACTOR

        # Resize the image
        resized_image = image.resize((new_width, new_height))

        # Compress the image as JPEG
        compressed_image = io.BytesIO()
        resized_image.save(compressed_image, 'JPEG', quality=JPEG_QUALITY)

    # Get the compressed image data
    compressed_image_data = compressed_image.getvalue()

    # Encode the compressed image data as base64
    encoded_image_data = compressed_image_data.hex()

    # Prepare the MicroPython payload
    payload = f"""
import display
import ubinascii

# Decode the compressed image data
compressed_image_data = ubinascii.unhexlify('{encoded_image_data}')

# Create a memory stream from the compressed image data
stream = io.BytesIO(compressed_image_data)

# Decode the JPEG image
image = ujpeg.decode(stream)

# Display the image on the Monocle
display.show(image)

# Close the stream to free up memory
stream.close()

# Explicitly delete variables to free up memory
del compressed_image_data, stream, image

# Run garbage collection to reclaim memory
gc.collect()
"""

    return payload

async def send_image_to_monocle(image_path):
    # Prepare the image payload
    payload = prepare_image_payload(image_path)

    # Create a Monocle instance
    mono = Monocle()

    async with mono:
        # Send the payload to the Monocle
        await mono.send(payload)

# Usage example
image_path = 'example.jpg'
asyncio.run(send_image_to_monocle(image_path))
