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
