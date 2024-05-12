import pygame
import threading
from modules.conversate_app import ConversateApp
from modules.database import create_interactions_table, check_missing_journal_entries
from modules.api import app  # Import the app variable from modules.api

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
    conversate_app = ConversateApp(screen)  # Rename the variable to avoid confusion

    print("Ready.")
    # Run the application
    conversate_app.run()

    # Clean up
    pygame.quit()

def run_api():
    app.run(port=5000)

if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api)
    api_thread.start()
    main()