import pygame
import time
import asyncio
import platform
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speed Typing Car")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 139)
PURPLE = (128, 0, 128)
DARK_PURPLE = (75, 0, 75)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
SKY_BLUE = (135, 206, 235)
SKY_ORANGE = (255, 165, 0)
CLOUD_WHITE = (240, 240, 240)
SUN_YELLOW = (255, 255, 0)
WINDOW_GRAY = (200, 200, 200)
BUILDING_GRAY = (100, 100, 100)
BUILDING_BROWN = (139, 69, 19)
ROAD_GRAY = (70, 70, 70)
CAR_SILVER = (192, 192, 192)
CAR_BLACK = (0, 0, 0)
CORAL = (255, 127, 80)
LAVENDER = (230, 230, 250)
DARK_BROWN = (101, 67, 33)
REDISH_BROWN = (165, 42, 42)

# Font
font = pygame.font.SysFont("Trebuchet MS", 25)

# Game variables
sentences = [
    "The sun sets slowly behind the mountain, casting a warm golden glow over the serene valley below.",
    "A skilled programmer writes code that is both efficient and easy to understand for future developers.",
    "Exploring the vast universe, astronauts discover new planets and marvel at the beauty of distant stars.",
    "In the quiet forest, the sound of rustling leaves and chirping birds creates a peaceful atmosphere."
]
current_sentence = ""
user_input = ""
car_x = 50
car_y = HEIGHT - 100
target_car_x = 50
car_speed = 0
start_time = 0
game_state = "playing"
wpm = 0
timer = 0
TIME_LIMIT = 30
cloud_positions = [(100, 80), (300, 120), (600, 100)]
cloud_base_speed = 0.5
city_cars = [(100, HEIGHT - 150), (300, HEIGHT - 150), (500, HEIGHT - 150), (700, HEIGHT - 150)]
city_car_speed = 1.0
random_cars = []
MAX_RANDOM_CARS = 6
sun_x = 50
sun_y = 70
SMOOTHING_FACTOR = 0.1
CRASH_COLOR = (255, 165, 0)
frame_count = 0  # For fire effect toggle

def setup():
    global current_sentence, user_input, car_x, target_car_x, start_time, game_state, wpm, timer, cloud_positions, city_cars, sun_x, random_cars, frame_count
    current_sentence = random.choice(sentences)
    user_input = ""
    car_x = 50
    target_car_x = 50
    start_time = time.time()
    game_state = "playing"
    wpm = 0
    timer = 0
    cloud_positions = [(100, 80), (300, 120), (600, 100)]
    city_cars = [(100, HEIGHT - 150), (300, HEIGHT - 150), (500, HEIGHT - 150), (700, HEIGHT - 150)]
    random_cars = []
    for _ in range(random.randint(3, MAX_RANDOM_CARS)):
        x = random.randint(0, WIDTH - 40)
        y = random.choice([HEIGHT - 150, HEIGHT - 200])
        direction = random.choice([(1, 0), (-1, 0)])
        color = random.choice([CAR_SILVER, CAR_BLACK])
        random_cars.append((x, y, direction, color))
    sun_x = 50
    frame_count = 0

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        test_surface = font.render(test_line, True, BLACK)
        if test_surface.get_width() <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines

def draw_text(text, y, color=BLACK, size=25, wrap=False):
    font_render = pygame.font.SysFont("Trebuchet MS", size)
    if wrap:
        lines = wrap_text(text, font_render, WIDTH - 100)
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, y + i * (size + 5)))
            screen.blit(text_surface, text_rect)
    else:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, y))
        screen.blit(text_surface, text_rect)

def interpolate_color(start_color, end_color, t):
    return (
        int(start_color[0] + (end_color[0] - start_color[0]) * t),
        int(start_color[1] + (end_color[1] - start_color[1]) * t),
        int(start_color[2] + (end_color[2] - start_color[2]) * t)
    )

def draw_background():
    t = min(timer / TIME_LIMIT, 1.0)
    sky_color = interpolate_color(SKY_BLUE, SKY_ORANGE, t)
    building_positions = [
        (0, HEIGHT // 2 - 100, 80, 100, BUILDING_GRAY),
        (80, HEIGHT // 2 - 150, 80, 150, BUILDING_BROWN),
        (160, HEIGHT // 2 - 120, 80, 120, BUILDING_GRAY),
        (240, HEIGHT // 2 - 80, 80, 80, BUILDING_BROWN),
        (320, HEIGHT // 2 - 130, 80, 130, BUILDING_GRAY),
        (400, HEIGHT // 2 - 100, 80, 100, BUILDING_GRAY),
        (480, HEIGHT // 2 - 150, 80, 150, BUILDING_BROWN),
        (560, HEIGHT // 2 - 120, 80, 120, BUILDING_GRAY),
        (640, HEIGHT // 2 - 80, 80, 80, BUILDING_BROWN),
        (720, HEIGHT // 2 - 130, 80, 130, BUILDING_GRAY)
    ]
    for x, y, w, h, color in building_positions:
        pygame.draw.rect(screen, color, (x, y, w, h))
        for win_x in range(x + 10, x + w - 10, 20):
            for win_y in range(y + 10, y + h - 10, 20):
                pygame.draw.rect(screen, WINDOW_GRAY, (win_x, win_y, 10, 10))
    lower_buildings = [
        (0, HEIGHT - 100, 60, 80, BUILDING_GRAY),
        (60, HEIGHT - 120, 60, 100, BUILDING_BROWN),
        (120, HEIGHT - 90, 60, 70, BUILDING_GRAY),
        (180, HEIGHT - 110, 60, 90, BUILDING_BROWN),
        (240, HEIGHT - 130, 60, 110, BUILDING_GRAY),
        (300, HEIGHT - 100, 60, 80, BUILDING_BROWN),
        (360, HEIGHT - 120, 60, 100, BUILDING_GRAY),
        (420, HEIGHT - 90, 60, 70, BUILDING_BROWN),
        (480, HEIGHT - 110, 60, 90, BUILDING_GRAY),
        (540, HEIGHT - 130, 60, 110, BUILDING_BROWN),
        (600, HEIGHT - 100, 60, 80, BUILDING_GRAY),
        (660, HEIGHT - 120, 60, 100, BUILDING_BROWN),
        (720, HEIGHT - 90, 60, 70, BUILDING_GRAY)
    ]
    for x, y, w, h, color in lower_buildings:
        pygame.draw.rect(screen, color, (x, y, w, h))
        for win_x in range(x + 5, x + w - 5, 15):
            for win_y in range(y + 5, y + h - 5, 15):
                pygame.draw.rect(screen, WINDOW_GRAY, (win_x, win_y, 8, 8))
    pygame.draw.rect(screen, ROAD_GRAY, (0, HEIGHT - 150, WIDTH, 150))
    pygame.draw.rect(screen, ROAD_GRAY, (0, HEIGHT - 250, WIDTH, 100))
    for y in range(HEIGHT - 140, HEIGHT - 10, 50):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y), 2)
    for y in range(HEIGHT - 240, HEIGHT - 150, 50):
        pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y), 2)

def draw_car(x, y, color, crashed=False):
    if not crashed or game_state != "crashed":
        pygame.draw.polygon(screen, color, [
            (x, y + 12), (x + 40, y + 12), (x + 30, y), (x + 10, y)
        ])
        pygame.draw.rect(screen, DARK_PURPLE if color == PURPLE else DARK_GRAY if color == CAR_BLACK else DARK_BLUE, (x, y + 12, 40, 10))
        pygame.draw.polygon(screen, WINDOW_GRAY, [
            (x + 15, y + 5), (x + 25, y + 5), (x + 25, y - 5), (x + 15, y - 5)
        ])
        pygame.draw.circle(screen, BLACK, (int(x + 10), y + 17), 6)
        pygame.draw.circle(screen, BLACK, (int(x + 30), y + 17), 6)
        pygame.draw.circle(screen, GRAY, (int(x + 10), y + 17), 3)
        pygame.draw.circle(screen, GRAY, (int(x + 30), y + 17), 3)
    else:
        global frame_count
        frame_count += 1
        # Blend car color with fire effect, ensuring valid integers
        fire_factor = random.uniform(0.3, 0.7) if frame_count % 10 < 5 else 0  # Flicker effect
        fire_color = (
            max(0, min(255, int(PURPLE[0] + (SKY_ORANGE[0] - PURPLE[0]) * fire_factor + (RED[0] - PURPLE[0]) * fire_factor * 0.5))),
            max(0, min(255, int(PURPLE[1] + (SKY_ORANGE[1] - PURPLE[1]) * fire_factor + (RED[1] - PURPLE[1]) * fire_factor * 0.5))),
            max(0, min(255, int(PURPLE[2] + (SKY_ORANGE[2] - PURPLE[2]) * fire_factor + (RED[2] - PURPLE[2]) * fire_factor * 0.5)))
        )
        pygame.draw.polygon(screen, fire_color, [
            (x, y + 12), (x + 40, y + 12), (x + 30, y), (x + 10, y)
        ])
        # Internal flames
        for _ in range(3):  # Three internal flames
            flame_x = x + random.randint(5, 35)  # Inside car body
            flame_y = y + random.randint(5, 15)  # Lower part of car
            base_color = SUN_YELLOW
            tip_color = RED if frame_count % 20 < 10 else SKY_ORANGE
            mid_color = (
                max(0, min(255, int(base_color[0] + (tip_color[0] - base_color[0]) * 0.5))),
                max(0, min(255, int(base_color[1] + (tip_color[1] - base_color[1]) * 0.5))),
                max(0, min(255, int(base_color[2] + (tip_color[2] - base_color[2]) * 0.5)))
            )
            flame_points = [
                (flame_x, flame_y),
                (flame_x + random.randint(2, 8), flame_y - random.randint(5, 10)),
                (flame_x + random.randint(-2, 2), flame_y - random.randint(7, 12))
            ]
            pygame.draw.polygon(screen, mid_color, flame_points)
            tip_points = [
                (flame_x + random.randint(2, 8), flame_y - random.randint(5, 10)),
                (flame_x + random.randint(-2, 2), flame_y - random.randint(7, 12)),
                (flame_x + random.randint(0, 5), flame_y - random.randint(8, 15))
            ]
            pygame.draw.polygon(screen, tip_color, tip_points)
        # Keep underbody and wheels
        pygame.draw.rect(screen, DARK_PURPLE if color == PURPLE else DARK_GRAY if color == CAR_BLACK else DARK_BLUE, (x, y + 12, 40, 10))
        pygame.draw.polygon(screen, WINDOW_GRAY, [
            (x + 15, y + 5), (x + 25, y + 5), (x + 25, y - 5), (x + 15, y - 5)
        ])
        pygame.draw.circle(screen, BLACK, (int(x + 10), y + 17), 6)
        pygame.draw.circle(screen, BLACK, (int(x + 30), y + 17), 6)
        pygame.draw.circle(screen, GRAY, (int(x + 10), y + 17), 3)
        pygame.draw.circle(screen, GRAY, (int(x + 30), y + 17), 3)

def calculate_wpm():
    global wpm, start_time
    elapsed_time = min(time.time() - start_time, TIME_LIMIT)
    if elapsed_time > 0 and game_state == "playing":
        # Count correctly typed characters
        correct_length = 0
        for i in range(min(len(user_input), len(current_sentence))):
            if user_input[i] == current_sentence[i]:
                correct_length += 1
        # Estimate words (assuming 5 characters per word)
        estimated_words = correct_length / 5
        wpm = (estimated_words / elapsed_time) * 60
    elif game_state in ["crashed", "won", "timed_out"]:
        # Use final correct length for end states
        correct_length = 0
        for i in range(min(len(user_input), len(current_sentence))):
            if user_input[i] == current_sentence[i]:
                correct_length += 1
        estimated_words = correct_length / 5
        wpm = (estimated_words / elapsed_time) * 60 if elapsed_time > 0 else 0
    return max(0, wpm)  # Ensure WPM is not negative

def update_loop():
    global car_x, target_car_x, game_state, user_input, wpm, timer, cloud_positions, city_cars, sun_x, random_cars
    if game_state == "playing":
        timer = time.time() - start_time
        if timer >= TIME_LIMIT:
            game_state = "timed_out"
            wpm = calculate_wpm()
            return
        progress = len(user_input) / len(current_sentence) if current_sentence else 0
        target_car_x = 50 + progress * (WIDTH - 130)
        car_x += (target_car_x - car_x) * SMOOTHING_FACTOR
        wpm = calculate_wpm()
        dynamic_cloud_speed = cloud_base_speed + wpm * 0.05
        dynamic_city_car_speed = city_car_speed + wpm * 0.1
        cloud_positions = [(x + dynamic_cloud_speed, y) for x, y in cloud_positions]
        cloud_positions = [(x % WIDTH, y) if x > WIDTH else (x, y) for x, y in cloud_positions]
        city_cars = [(x - dynamic_city_car_speed, y) for x, y in city_cars]
        city_cars = [(x + WIDTH, y) if x < -40 else (x, y) for x, y in city_cars]
        for i, (x, y, (dx, dy), color) in enumerate(random_cars):
            x += dx * 2
            if x < -40:
                x = WIDTH
            elif x > WIDTH:
                x = -40
            random_cars[i] = (x, y, (dx, dy), color)
        if user_input and user_input != current_sentence[:len(user_input)]:
            game_state = "crashed"  # End game immediately on wrong input
            wpm = calculate_wpm()
        if user_input == current_sentence:
            game_state = "won"
            wpm = calculate_wpm()

def draw():
    t = min(timer / TIME_LIMIT, 1.0)
    sky_color = interpolate_color(SKY_BLUE, SKY_ORANGE, t)
    screen.fill(sky_color)
    draw_background()
    sun_color = interpolate_color(SUN_YELLOW, CLOUD_WHITE, t)
    pygame.draw.circle(screen, sun_color, (sun_x, sun_y), 30)
    for x, y in cloud_positions:
        pygame.draw.circle(screen, CLOUD_WHITE, (int(x), y), 20)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(x + 30), y - 10), 25)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(x + 60), y), 20)
    # Draw timer with oval background
    timer_text = f"{max(0, TIME_LIMIT - timer):.1f}s"
    timer_surface = font.render(timer_text, True, BLUE)
    timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 20))
    # Create an oval background
    bg_width = timer_rect.width + 20  # Wider padding
    bg_height = timer_rect.height + 10  # Standard height padding
    bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
    pygame.draw.ellipse(bg_surface, (128, 128, 128, 128), (0, 0, bg_width, bg_height))  # Semi-transparent gray
    screen.blit(bg_surface, (timer_rect.centerx - bg_width // 2, timer_rect.centery - bg_height // 2))
    screen.blit(timer_surface, timer_rect)
    lines = wrap_text(current_sentence, font, WIDTH - 100)
    total_height = len(lines) * 30
    start_y = 100
    if start_y + total_height > HEIGHT - 250:
        start_y = max(50, HEIGHT - 250 - total_height)
    total_chars = 0
    for i, line in enumerate(lines):
        y_offset = start_y + i * 30
        if i == 0:
            line_start = 0
        else:
            prev_text = " ".join(wrap_text(current_sentence, font, WIDTH - 100)[:i])
            line_start = len(prev_text) + 1
        for j, char in enumerate(line):
            global_index = line_start + j
            if global_index < len(user_input):
                if user_input[global_index] == char:
                    color = SUN_YELLOW
                else:
                    color = RED
            else:
                color = BLACK
            text_surface = font.render(char, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2 - (len(line) * 12 // 2) + j * 12, y_offset))
            screen.blit(text_surface, text_rect)
        total_chars += len(line)
    draw_car(car_x, car_y, PURPLE, game_state == "crashed")
    for x, y in city_cars:
        car_color = CAR_SILVER if city_cars.index((x, y)) % 2 == 0 else CAR_BLACK
        draw_car(x, y, car_color)
    for x, y, _, color in random_cars:
        draw_car(x, y, color)
    if game_state in ["crashed", "won", "timed_out"]:
        messages = []
        if game_state == "crashed":
            messages.append(("Game Over!", RED, 50))
        elif game_state == "won":
            messages.append(("You Win!", BLACK, 35))
        elif game_state == "timed_out":
            messages.append(("Time's Up!", RED, 50))
        messages.append((f"WPM: {wpm:.1f}", BLACK, 35))
        messages.append(("Press R to Restart", BLACK, 25))
        total_message_height = len(messages) * 35 + (len(messages) - 1) * 10
        start_y = ((HEIGHT - total_message_height) // 2) + 50
        for i, (text, color, size) in enumerate(messages):
            text_surface = pygame.font.SysFont("Trebuchet MS", size).render(text, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, start_y + i * 45))
            if text in ["Game Over!", "Time's Up!"]:
                bg_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 10))  # Padding of 10px
                bg_surface.set_alpha(128)  # Semi-transparent (0-255)
                bg_surface.fill(BLACK)
                bg_rect = bg_surface.get_rect(center=(WIDTH // 2, start_y + i * 45))
                screen.blit(bg_surface, bg_rect)
            screen.blit(text_surface, text_rect)
    pygame.display.flip()

async def main():
    global user_input, game_state, timer
    setup()
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if game_state == "playing":
                    if event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    elif event.key == pygame.K_RETURN and user_input == current_sentence:
                        game_state = "won"
                        wpm = calculate_wpm()
                    elif event.unicode.isprintable():
                        user_input += event.unicode
                        update_loop()  # Check for wrong input immediately
                elif event.key == pygame.K_r and game_state in ["crashed", "won", "timed_out"]:
                    setup()
        update_loop()
        draw()
        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())