# home_screen.py

import pygame
import sys
from support import BLACK, DARK_GREY, GREEN, RED, WHITE, BACKGROUND_COLOR, LIGHT_GREY, GAME_LEVELS, screen_height, screen_width, sidebar_width
from game_page import draw_button, pixelated_font

# Initialize Pygame
pygame.init()

def draw_home_screen(screen, stats):
    global screen_width, screen_height, sidebar_width
    screen.fill(BACKGROUND_COLOR)
    font_large = pygame.font.Font('fonts/pixelated_font.ttf', 72)
    font_small = pygame.font.Font('fonts/pixelated_font.ttf', 32)
    font_stats = pygame.font.Font('fonts/pixelated_font.ttf', 24)

    
    # Draw title centered at the top
    title_text = "MINESWEEPER"
    title_render = font_large.render(title_text, True, WHITE)
    screen.blit(title_render, ((screen_width - sidebar_width - title_render.get_width()) // 2, 50))

    # Draw level selection buttons centered
    button_width = 400
    button_height = 50
    button_padding = 20
    button_start_y = 200

    for i, (level, info) in enumerate(GAME_LEVELS.items()):
        button_x = (screen_width - sidebar_width - button_width) // 2
        button_y = button_start_y + i * (button_height + button_padding)
        pygame.draw.rect(screen, DARK_GREY, (button_x, button_y, button_width, button_height))
        pygame.draw.rect(screen, WHITE, (button_x, button_y, button_width, button_height), 2)
        level_text = f"{level.capitalize()} - {info['width']}x{info['height']} - {info['mines']} Mines"
        text_render = font_small.render(level_text, True, GREEN)
        text_rect = text_render.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        screen.blit(text_render, text_rect)

    # Draw stats sidebar
    sidebar_x = screen_width - sidebar_width
    pygame.draw.rect(screen, LIGHT_GREY, (sidebar_x, 0, sidebar_width, screen_height))
    pygame.draw.rect(screen, WHITE, (sidebar_x, 0, sidebar_width, screen_height), 2)
    
    # Draw "STATS" heading
    stats_heading_font = pygame.font.Font('fonts/pixelated_font.ttf', 48)
    stats_heading_text = "STATS"
    stats_heading_render = stats_heading_font.render(stats_heading_text, True, BLACK)
    screen.blit(stats_heading_render, (sidebar_x + (sidebar_width - stats_heading_render.get_width()) // 2, 60))
    
    stats_start_y = 140
    for i, level in enumerate(GAME_LEVELS):
        stats_text_y = stats_start_y + i * 100
        level_render = font_small.render(level.capitalize(), True, BLACK)
        screen.blit(level_render, (sidebar_x + 10, stats_text_y))
        if level in stats:
            win_percentage = (stats[level]['wins'] / stats[level]['total']) * 100 if stats[level]['total'] > 0 else 0
            stats_text = f"Wins: {stats[level]['wins']} / {stats[level]['total']} ({win_percentage:.2f}%)"
            best_time_text = f"Best Time: {stats[level]['best_time']:.2f}s" if stats[level]['best_time'] is not None else "Best Time: N/A"
            stats_render = font_stats.render(stats_text, True, BLACK)
            best_time_render = font_stats.render(best_time_text, True, BLACK)
            screen.blit(stats_render, (sidebar_x + 10, stats_text_y + 30))
            screen.blit(best_time_render, (sidebar_x + 10, stats_text_y + 60))
        else:
            stats_render = font_stats.render("Wins: 0 / 0 (0.00%)", True, WHITE)
            best_time_render = font_stats.render("Best Time: N/A", True, WHITE)
            screen.blit(stats_render, (sidebar_x + 10, stats_text_y + 30))
            screen.blit(best_time_render, (sidebar_x + 10, stats_text_y + 60))
    
    # Draw quit button centered at the bottom
    quit_button_width = 200
    quit_button_height = 50
    quit_button_x = (screen_width - sidebar_width - quit_button_width) // 2
    quit_button_y = screen_height - 100
    pygame.draw.rect(screen, LIGHT_GREY, (quit_button_x, quit_button_y, quit_button_width, quit_button_height))
    pygame.draw.rect(screen, WHITE, (quit_button_x, quit_button_y, quit_button_width, quit_button_height), 2)
    quit_text = "QUIT"
    quit_render = font_small.render(quit_text, True, RED)
    quit_text_rect = quit_render.get_rect(center=(quit_button_x + quit_button_width // 2, quit_button_y + quit_button_height // 2))
    screen.blit(quit_render, quit_text_rect)

    pygame.display.flip()

def handle_home_screen_events():
    global screen_width, screen_height
    resizing = False
    resize_event = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.w, event.h
            resizing = True
            resize_event = event
        elif event.type == pygame.MOUSEBUTTONUP:
            if resizing:
                resizing = False
                return resize_event

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                
                # Check if quit button is clicked
                quit_button_width = 200
                quit_button_height = 50
                quit_button_x = (screen_width - sidebar_width - quit_button_width) // 2
                quit_button_y = screen_height - 100
                if quit_button_x <= mouse_x <= quit_button_x + quit_button_width and quit_button_y <= mouse_y <= quit_button_y + quit_button_height:
                    pygame.quit()
                    sys.exit()

                # Check if level buttons are clicked
                button_width = 400
                button_height = 50
                button_padding = 20
                button_start_y = 200
                for i, level in enumerate(GAME_LEVELS):
                    button_x = (screen_width - sidebar_width - button_width) // 2
                    button_y = button_start_y + i * (button_height + button_padding)
                    if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                        return level

    return None

def run_home_screen(stats):
    global screen_width, screen_height
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("MINESWEEPER - Home")

    while True:
        draw_home_screen(screen, stats)
        event_result = handle_home_screen_events()
        if isinstance(event_result, pygame.event.Event) and event_result.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        elif event_result:
            return event_result

if __name__ == "__main__":
    run_home_screen({})
