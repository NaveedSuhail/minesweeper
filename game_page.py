# gampage.py

import pygame
import sys
import random
import time
from support import *

# Initialize Pygame
pygame.init()

# Load 3D textures
tile_texture = pygame.image.load('textures/tile.png')
mine_texture = pygame.image.load('textures/mine.png')
flag_texture = pygame.image.load('textures/flag.png')

# Load pixelated font
pixelated_font = pygame.font.Font('fonts/pixelated_font.ttf', 24)

# Initial font size for the game over/won message
message_font_size = 24

def initialize_grid(level):
    global GRID_WIDTH, GRID_HEIGHT, NUM_MINES, grid, revealed, non_mine_tiles
    GRID_WIDTH, GRID_HEIGHT, NUM_MINES = GAME_LEVELS[level].values()
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    revealed = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    non_mine_tiles = (GRID_WIDTH * GRID_HEIGHT) - NUM_MINES
    mines = set()
    while len(mines) < NUM_MINES:
        x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in mines:
            mines.add((x, y))
            grid[y][x] = -1
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            if tile != -1:
                grid[y][x] = count_adjacent_mines(x, y)

def place_mines():
    global mines, grid
    mines = set()
    
    while len(mines) < NUM_MINES:
        x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in mines:
            mines.add((x, y))
            grid[y][x] = -1

def count_adjacent_mines(x, y):
    count = 0
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[ny][nx] == -1:
                count += 1
    return count

def reveal_tile(x, y):
    global num_revealed, game_over, game_won, elapsed_time, start_time
    if revealed[y][x] or game_over or game_won:
        return
    
    revealed[y][x] = True
    num_revealed += 1
    
    if grid[y][x] == 0:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    reveal_tile(nx, ny)
    
    if grid[y][x] == -1:
        game_over = True
        reveal_mines()
        elapsed_time = int(time.time() - start_time) if start_time else 0
        start_time = None  # Stop the timer when the game is lost
        save_stats(current_level, 'loss', elapsed_time)
    elif num_revealed == non_mine_tiles:
        game_won = True
        elapsed_time = int(time.time() - start_time) if start_time else 0
        start_time = None  # Stop the timer when the game is won
        save_stats(current_level, 'win', elapsed_time)
        
def reveal_mines():
    for x, y in mines:
        revealed[y][x] = True

def draw_grid(screen, grid_width, grid_height, tile_size, padding_x, padding_y):
    for x in range(grid_width):
        for y in range(grid_height):
            rect_x = round(x * tile_size * zoom + padding_x - scroll_x)
            rect_y = round(y * tile_size * zoom + padding_y - scroll_y)
            rect_width = round(tile_size * zoom)
            rect_height = round(tile_size * zoom)
            rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
            if 0 <= x < grid_width and 0 <= y < grid_height:
                if revealed[y][x]:
                    if grid[y][x] == -1:
                        screen.blit(pygame.transform.scale(mine_texture, (rect_width, rect_height)), rect)
                    else:
                        screen.blit(pygame.transform.scale(tile_texture, (rect_width, rect_height)), rect)
                        if grid[y][x] > 0:
                            text = pixelated_font.render(str(grid[y][x]), True, WHITE)
                            text_rect = text.get_rect(center=rect.center)
                            screen.blit(text, text_rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                    if (x, y) in flags:
                        flag_center = (rect.centerx, rect.centery)
                        screen.blit(pygame.transform.scale(flag_texture, (int(tile_size * zoom * 0.4), int(tile_size * zoom * 0.4))), (flag_center[0] - int(tile_size * zoom * 0.2), flag_center[1] - int(tile_size * zoom * 0.2)))
            pygame.draw.rect(screen, WHITE, rect, 1)

def draw_interface(screen):
    global elapsed_time, game_over, game_won, message_font_size

    # Initialize or increment message_font_size
    if not (game_over or game_won):
        message_font_size = 24  # Reset font size when game is active
    else:
        if message_font_size < 72:
            message_font_size += 1  # Increase font size when game is over
        else:
            message_font_size = 72  # Cap font size at 72

    # Calculate positions for interface elements
    font = pixelated_font
    time_position = (20, 20)
    fraction_text = f"Progress: {num_revealed}/{non_mine_tiles} ({int(num_revealed / non_mine_tiles * 100)}%)"
    fraction_position = ((screen_width - font.render(fraction_text, True, WHITE).get_width()) // 2, 20)
    flags_text = f"Flags: {len(flags)} / {NUM_MINES}"
    flags_position = (screen_width - font.render(flags_text, True, WHITE).get_width() - 20, 20)

    # Draw a semi-transparent background for the interface
    interface_background_color = DARK_GREY  # Dark gray with some transparency
    interface_background_rect = pygame.Rect(0, 0, screen_width, 60)
    pygame.draw.rect(screen, interface_background_color, interface_background_rect)

    # Draw the timer
    if start_time:
        elapsed_time = int(time.time() - start_time)
    time_text = f"Time: {elapsed_time} s"
    screen.blit(font.render(time_text, True, RED), time_position)

    # Draw non-mine tiles revealed fraction
    screen.blit(font.render(fraction_text, True, GREEN), fraction_position)

    # Draw number of flags marked / Total number of mines
    screen.blit(font.render(flags_text, True, RED), flags_position)

    # Draw game status text with growing size
    if game_over or game_won:
        message_font = pygame.font.Font('fonts/pixelated_font.ttf', message_font_size)
        game_text = "Game Over! You hit a mine." if game_over else "Congratulations! You won."
        game_text_color = RED if game_over else DARK_GREEN
        game_text_render = message_font.render(game_text, True, game_text_color)
        game_text_rect = game_text_render.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(game_text_render, game_text_rect)

    draw_button(screen, font, "Exit to Main Menu", 20, screen_height - 70, 250, 50)
    draw_button(screen, font, "Regenerate Game", screen_width - 250 - 20, screen_height - 70, 250, 50)

    pygame.display.flip()

def draw_button(screen, font, text, x, y, width, height):
    button_background_color = DARK_GREY  # Dark gray background
    pygame.draw.rect(screen, button_background_color, (x, y, width, height))
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)
    text_surface = font.render(text, True, RED)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

def center_grid():
    global screen_width, screen_height, scroll_x, scroll_y
    screen_width, screen_height = screen.get_size()

def main_game(level):
    global screen, screen_width, screen_height, GRID_WIDTH, GRID_HEIGHT, NUM_MINES, non_mine_tiles, grid, revealed, flags, avoid_first_click, game_over, game_won, start_time, elapsed_time, num_revealed, scroll_x, scroll_y, dragging, current_level
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("MINESWEEPER - Game")
    
    current_level = level  # Set current level to the chosen level
    initialize_grid(level)
    
    game_over = False
    game_won = False
    start_time = None  # Reset start_time at the beginning of each game
    elapsed_time = 0
    num_revealed = 0
    flags = set()
    
    avoid_first_click = True
    dragging = False  # Initialize dragging flag
    
    game_state = 'playing'  # Introduce a game state variable
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not game_won:
                    elapsed_time = int(time.time() - start_time) if start_time else 0
                    save_stats(level, 'loss', elapsed_time)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                center_grid()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not game_won:
                        elapsed_time = int(time.time() - start_time) if start_time else 0
                        save_stats(level, 'loss', elapsed_time)
                    return 'home'  # Signal to return to home
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    handle_left_click(event)
                elif event.button == 3:  # Right click (flagging)
                    handle_right_click(event)
                elif event.button == 4:  # Scroll up (zoom in)
                    zoom_in()
                elif event.button == 5:  # Scroll down (zoom out)
                    zoom_out()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    handle_left_click_release(event)
                    
                    # Check if exit button is clicked
                    exit_button_rect = pygame.Rect(20, screen_height - 70, 250, 50)
                    if exit_button_rect.collidepoint(event.pos):
                        if not game_won:
                            elapsed_time = int(time.time() - start_time) if start_time else 0
                            save_stats(level, 'loss', elapsed_time)
                        return 'home'  # Signal to return to home
                    
                    # Check if regenerate button is clicked
                    regenerate_button_rect = pygame.Rect(screen_width - 270, screen_height - 70, 250, 50)
                    if regenerate_button_rect.collidepoint(event.pos):
                        if not game_won:
                            elapsed_time = int(time.time() - start_time) if start_time else 0
                            save_stats(level, 'loss', elapsed_time)                        
                        main_game(level)  # Regenerate game

            elif event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(event)
        
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, GRID_WIDTH, GRID_HEIGHT, TILE_SIZE, (screen_width - GRID_WIDTH * TILE_SIZE * zoom) // 2, (screen_height - GRID_HEIGHT * TILE_SIZE * zoom) // 2)
        draw_interface(screen)
        
        if game_over:
            game_state = 'loss'  # Set game state to 'loss'

        if game_won:
            game_state = 'win'  # Set game state to 'win'
        
        pygame.display.flip()

def handle_left_click(event):
    global dragging, drag_start_x, drag_start_y, scroll_start_x, scroll_start_y
    dragging = True
    drag_start_x, drag_start_y = event.pos
    scroll_start_x, scroll_start_y = scroll_x, scroll_y

def handle_left_click_release(event):
    global dragging, avoid_first_click, start_time
    dragging = False
    if avoid_first_click:
        avoid_first_click = False
        return
    mouse_x, mouse_y = event.pos
    grid_x = int((mouse_x + scroll_x - (screen_width - GRID_WIDTH * TILE_SIZE * zoom) // 2) / (TILE_SIZE * zoom))
    grid_y = int((mouse_y + scroll_y - (screen_height - GRID_HEIGHT * TILE_SIZE * zoom) // 2) / (TILE_SIZE * zoom))
    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        if not revealed[grid_y][grid_x] and (grid_x, grid_y) not in flags:
            if not game_over and start_time is None:  # Initialize start_time only if game is not over
                start_time = time.time()
            reveal_tile(grid_x, grid_y)

def handle_right_click(event):
    global flags
    mouse_x, mouse_y = event.pos
    grid_x = int((mouse_x + scroll_x - (screen_width - GRID_WIDTH * TILE_SIZE * zoom) // 2) / (TILE_SIZE * zoom))
    grid_y = int((mouse_y + scroll_y - (screen_height - GRID_HEIGHT * TILE_SIZE * zoom) // 2) / (TILE_SIZE * zoom))
    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        if not revealed[grid_y][grid_x]:
            if (grid_x, grid_y) in flags:
                flags.remove((grid_x, grid_y))
            else:
                flags.add((grid_x, grid_y))

def zoom_in():
    global zoom, scroll_x, scroll_y
    zoom = min(zoom + zoom_step, max_zoom)
    scroll_x = int(scroll_x * (1 + zoom_step))
    scroll_y = int(scroll_y * (1 + zoom_step))

def zoom_out():
    global zoom, scroll_x, scroll_y
    zoom = max(zoom - zoom_step, min_zoom)
    scroll_x = int(scroll_x * (1 - zoom_step))
    scroll_y = int(scroll_y * (1 - zoom_step))

def handle_mouse_motion(event):
    global scroll_x, scroll_y, dragging
    if dragging:
        mouse_x, mouse_y = event.pos
        scroll_x = scroll_start_x - (mouse_x - drag_start_x)
        scroll_y = scroll_start_y - (mouse_y - drag_start_y)

if __name__ == "__main__":
    main_game("beginner")
