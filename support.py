# support.py

import csv
from datetime import datetime

################# Constants #################
TILE_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 20
NUM_MINES = 80

# Colors
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (80, 80, 80)
LIGHT_GREY = (180, 180, 180)
DARK_GREY = (60, 60, 60, 150) 
RED = (200, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0, 200)
BLACK = (0, 0, 0)

# Game levels
GAME_LEVELS = {level: {"width": w, "height": h, "mines": m} for level, (w, h, m) in (
    ("mini", (6, 6, 6)),
    ("beginner", (10, 10, 15)),
    ("easy", (15, 15, 40)),
    ("medium", (20, 20, 80)),
    ("hard", (25, 25, 150)),
    ("expert", (30, 30, 270)),
    ("massive", (40, 40, 400)),
)}

# Initial screen dimensions
screen_width, screen_height = 1000, 850
sidebar_width = 300

# Variables for scroll and zoom
scroll_x, scroll_y = 0, 0
zoom = 1.0
min_zoom = 0.5
max_zoom = 2.0
zoom_step = 0.1

# Initialize grid and mines
grid = []
revealed = []
mines = set()
flags = set()

# Game state variables
game_over = False
game_won = False
start_time = None
elapsed_time = 0
num_revealed = 0

# Variables to handle dragging
dragging = False
drag_start_x, drag_start_y = 0, 0
scroll_start_x, scroll_start_y = 0, 0

# Flag to avoid double action on the same click
avoid_first_click = False


################# Functions #################
def save_stats(level, result, elapsed_time):
    if elapsed_time <= 0:
        return
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{current_date},{level},{result},{elapsed_time}\n"
    with open('stats.csv', 'a', encoding='utf-8') as file:
        file.write(line)

def load_game_stats():
    stats = {}
    try:
        with open('stats.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                date, level, result, elapsed_time = row
                if level not in stats:
                    stats[level] = {'total': 0, 'wins': 0, 'best_time': None}
                stats[level]['total'] += 1
                if result == 'win':
                    stats[level]['wins'] += 1
                    elapsed_time = float(elapsed_time)
                    if stats[level]['best_time'] is None or elapsed_time < stats[level]['best_time']:
                        stats[level]['best_time'] = elapsed_time
    except FileNotFoundError:
        pass
    return stats
