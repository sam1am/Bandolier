Output of tree command:
```
|-- .gitignore
|-- .summary_files
    |-- code_summary.md
    |-- previous_selection.json
|-- __pycache__
|-- area.py
|-- areas
    |-- area1
        |-- area.conf
        |-- lvl.png
        |-- lvl_mask.png
    |-- area2
        |-- area.conf
        |-- lvl.png
        |-- lvl_mask.png
    |-- area3
        |-- area.conf
        |-- lvl.png
        |-- lvl_mask.png
|-- constants.py
|-- main.py
|-- player.png
|-- requirements.txt
|-- sprites.py
|-- utilities.py
|-- venv
|-- wall.png

```

---

./constants.py
```
# constants.py

# Constants for the screen width and height
SCREEN_SIZE = (640, 480)

# Colors
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
```
---

./utilities.py
```
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
```
---

./sprites.py
```
# sprites.py

import pygame


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, x, y):
        super().__init__()
        self.image = pygame.image.load(image_file).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
```
---

./main.py
```
# main.py

import pygame
from constants import SCREEN_SIZE, BLACK
from sprites import Background
from utilities import check_walkability, within_bounds
from area import Area




def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()

    current_area = Area("areas/area1")

    print("Current area:", current_area.name)

    # Load the background and walkability layer images
    background = current_area.background
    walkability_layer = current_area.mask


    # Character's initial position
    character_position = pygame.math.Vector2(320, 450)

    hide_character = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Fill the screen with black
        screen.fill(BLACK)
        # Draw the background
        screen.blit(background.image, background.rect)
        # If the player presses an arrow key, move the character
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and within_bounds(character_position.x - 6, character_position.y, SCREEN_SIZE):
            new_position = character_position + (-5, 0)
            can_move, hide = check_walkability(
                *new_position, walkability_layer)
            if can_move:
                character_position = new_position
                hide_character = hide
        if keys[pygame.K_RIGHT] and within_bounds(character_position.x + 6, character_position.y, SCREEN_SIZE):
            new_position = character_position + (5, 0)
            can_move, hide = check_walkability(
                *new_position, walkability_layer)
            if can_move:
                character_position = new_position
                hide_character = hide
        if keys[pygame.K_UP] and within_bounds(character_position.x, character_position.y - 6, SCREEN_SIZE):
            new_position = character_position + (0, -5)
            can_move, hide = check_walkability(
                *new_position, walkability_layer)
            if can_move:
                character_position = new_position
                hide_character = hide
        if keys[pygame.K_DOWN] and within_bounds(character_position.x, character_position.y + 6, SCREEN_SIZE):
            new_position = character_position + (0, 5)
            can_move, hide = check_walkability(
                *new_position, walkability_layer)
            if can_move:
                character_position = new_position
                hide_character = hide

        edge_distance = 5

        if character_position.x <= edge_distance:
            # The player has moved west
            new_area_name = current_area.get_connecting_area("west")
            current_area = Area(f"areas/{new_area_name}")
            background = current_area.background
            walkability_layer = current_area.mask
            character_position.x = SCREEN_SIZE[0] - edge_distance

        elif character_position.x >= SCREEN_SIZE[0] - edge_distance:
            # The player has moved east
            new_area_name = current_area.get_connecting_area("east")
            current_area = Area(f"areas/{new_area_name}")
            background = current_area.background
            walkability_layer = current_area.mask
            character_position.x = edge_distance

        elif character_position.y <= edge_distance:
            # The player has moved north
            new_area_name = current_area.get_connecting_area("north")
            current_area = Area(f"areas/{new_area_name}")
            background = current_area.background
            walkability_layer = current_area.mask
            character_position.y = SCREEN_SIZE[1] - edge_distance

        elif character_position.y >= SCREEN_SIZE[1] - edge_distance:
            # The player has moved south
            new_area_name = current_area.get_connecting_area("south")
            current_area = Area(f"areas/{new_area_name}")
            background = current_area.background
            walkability_layer = current_area.mask
            character_position.y = edge_distance

        print("Character position:", character_position)
        print('Current area:', current_area.name)

        # Draw the character as a red circle, unless it should be hidden
        if not hide_character:
            pygame.draw.circle(screen, (255, 0, 0), (int(
                character_position.x), int(character_position.y)), 10)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
```
---

./area.py
```
import os
import pygame
from configparser import ConfigParser
from sprites import Background

class Area:

    def __init__(self, area_folder):
        # Load the configuration file for the area
        config = ConfigParser()
        config_path = os.path.join(area_folder, "area.conf")
        print("Loading area config file:", config_path)
        config.read(config_path)

        self.name = config.get("Area", "name")
        self.description = config.get("Area", "description")

        # Load the background image and mask
        self.background = Background(
            os.path.join(area_folder, "lvl.png"), 0, 0)

        self.mask = pygame.image.load(
            os.path.join(area_folder, "lvl_mask.png"))

        # Initialize connecting areas as None
        self.connecting_areas = {"north": None,
                                 "east": None, "south": None, "west": None}

        # Only set connecting areas if they exist in the config file
        if config.has_section("ConnectingAreas"):
            for direction in self.connecting_areas.keys():
                if config.has_option("ConnectingAreas", direction):
                    self.connecting_areas[direction] = config.get(
                        "ConnectingAreas", direction)

    def get_connecting_area(self, direction):
        print("Connecting to area: ", self.connecting_areas.get(direction))
        return self.connecting_areas.get(direction)
```
---

./areas/area1/area.conf
```
[Area]
name = Starting Area
description = This is the starting area.

[ConnectingAreas]
north = area2

```
---

./areas/area2/area.conf
```
[Area]
name = Area 2
description = This is the the second area.

[ConnectingAreas]
north = area3
south = area1

```
---
