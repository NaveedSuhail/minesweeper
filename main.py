# main.py

import pygame
from home_screen import run_home_screen
from game_page import main_game, load_game_stats
from datetime import datetime

# Initialize Pygame
pygame.init()

if __name__ == "__main__":
    home_screen = True
    stats = load_game_stats()
    while True:
        if home_screen:
            selected_level = run_home_screen(stats)
            if selected_level:
                home_screen = False
                result = main_game(selected_level)
                if result == 'home':
                    home_screen = True
                stats = load_game_stats()  # Reload stats after game
        else:
            home_screen = True
