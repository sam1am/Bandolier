import pygame

# Define some colors
WHITE = (255, 255, 255)

# Initialize Pygame
pygame.init()

# Load the emoji font
font = pygame.font.Font("NotoColorEmoji.ttf", 36)

# Create the screen
screen = pygame.display.set_mode((800, 600))

# Create a text surface and blit it onto the screen
text_surface = font.render("🚀", True, WHITE)
screen.blit(text_surface, (100, 100))

# Update the display
pygame.display.flip()

# Wait before quitting
pygame.time.wait(3000)

pygame.quit()

