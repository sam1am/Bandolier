import pygame
from modules.conversate_app import ConversateApp
from modules.database import create_interactions_table, check_missing_journal_entries

def main():
    create_interactions_table()
    check_missing_journal_entries()
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Conversate")

    # Create an instance of ConversateApp
    app = ConversateApp(screen)

    print("Ready.")
    # Run the application
    app.run()

    # Clean up
    pygame.quit()

if __name__ == "__main__":
    main()