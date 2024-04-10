# utilities.py

from constants import BLACK, WHITE, SCREEN_SIZE


def within_bounds(x, y, screen_size):
    return 0 <= x < screen_size[0] and 0 <= y < screen_size[1]


def check_walkability(x, y, walkability_layer):
    # If the position is outside of the screen bounds, it's walkable
    if not within_bounds(x, y, SCREEN_SIZE):
        return True, False

    # Get the color of the pixel at the given position
    pixel_color = walkability_layer.get_at((int(x), int(y)))

    # If the color is black, return False (not walkable)
    if pixel_color == BLACK:
        return False, False

    # If the color is white, the character should be hidden
    elif pixel_color == WHITE:
        return True, True

    # Otherwise, return True (walkable)
    return True, False
