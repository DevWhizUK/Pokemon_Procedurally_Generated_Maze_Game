import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200  # Increased width
SCREEN_HEIGHT = 800  # Increased height
TILE_SIZE = 20  # Reduced tile size

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
AMBER = (255, 191, 0)
BLUE = (0, 0, 255)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Game")

# Font for timer and messages
font = pygame.font.Font(None, 36)
message_font = pygame.font.Font(None, 72)

# Player class
class Player:
    def __init__(self, x, y, maze):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.color = BLUE
        self.maze = maze

    def move(self, dx, dy):
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        # Calculate grid position
        grid_x = new_x // TILE_SIZE
        grid_y = new_y // TILE_SIZE

        # Check if new position is within bounds and not a wall
        if 0 <= grid_x < len(self.maze[0]) and 0 <= grid_y < len(self.maze):
            if self.maze[grid_y][grid_x] == 0:
                self.rect.x = new_x
                self.rect.y = new_y

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Bomb class
class Bomb:
    def __init__(self, x, y, color, timer):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.color = color
        self.timer = timer
        self.start_time = None

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def start_countdown(self):
        if self.start_time is None:
            self.start_time = time.time()

    def is_exploded(self):
        if self.start_time and (time.time() - self.start_time >= self.timer):
            return True
        return False

# Maze generation function
def generate_maze(width, height, difficulty):
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def carve_passages(cx, cy):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                if (dx, dy) == (1, 0) or (dx, dy) == (-1, 0):
                    if nx + dx >= 0 and nx + dx < width and maze[ny][nx + dx] == 1:
                        maze[cy][cx] = 0
                        maze[ny][nx] = 0
                        maze[ny][nx + dx] = 0
                        carve_passages(nx + dx, ny)
                if (dx, dy) == (0, 1) or (dx, dy) == (0, -1):
                    if ny + dy >= 0 and ny + dy < height and maze[ny + dy][nx] == 1:
                        maze[cy][cx] = 0
                        maze[ny][nx] = 0
                        maze[ny + dy][nx] = 0
                        carve_passages(nx, ny + dy)

    carve_passages(0, 0)
    return maze

# Draw the maze
def draw_maze(surface, maze):
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] == 1:
                pygame.draw.rect(surface, BLACK, pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

# Draw the timer
def draw_timer(surface, start_time):
    elapsed_time = time.time() - start_time
    timer_text = font.render(f"Time: {elapsed_time:.2f} s", True, RED)
    surface.blit(timer_text, (SCREEN_WIDTH - 200, 10))

# Draw the level counter
def draw_level_counter(surface, level):
    level_text = font.render(f"Level: {level}", True, RED)
    surface.blit(level_text, (10, 10))

# Draw the success message
def draw_success_message(surface):
    message_text = message_font.render("Level Complete!", True, GREEN)
    text_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.blit(message_text, text_rect)

# Spawn bombs
def spawn_bombs(maze, num_bombs):
    bomb_types = [
        (GREEN, 4.0),
        (AMBER, 2.8),
        (RED, 2.0)
    ]
    bombs = []
    while len(bombs) < num_bombs:
        x = random.randint(0, len(maze[0]) - 1)
        y = random.randint(0, len(maze) - 1)
        if maze[y][x] == 0:
            color, timer = random.choice(bomb_types)
            bombs.append(Bomb(x, y, color, timer))
    return bombs

# Main function
def main():
    clock = pygame.time.Clock()
    performance_metrics = []
    level = 1

    def calculate_difficulty():
        if not performance_metrics:
            return 0.5  # Default difficulty
        avg_time = sum([m['time'] for m in performance_metrics]) / len(performance_metrics)
        avg_moves = sum([m['moves'] for m in performance_metrics]) / len(performance_metrics)
        return min(max((avg_time + avg_moves) / 200, 0.1), 1.0)

    while True:
        difficulty = calculate_difficulty()
        maze = generate_maze(SCREEN_WIDTH // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE, difficulty)
        player = Player(TILE_SIZE // 2, TILE_SIZE // 2, maze)
        goal_rect = pygame.Rect((SCREEN_WIDTH // TILE_SIZE - 1) * TILE_SIZE, (SCREEN_HEIGHT // TILE_SIZE - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        num_bombs = random.randint(2, 8)
        bombs = spawn_bombs(maze, num_bombs)

        start_time = time.time()
        moves = 0

        running = True
        show_success_message = False
        success_message_start_time = None

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                player.move(-TILE_SIZE, 0)
                moves += 1
            if keys[pygame.K_d]:
                player.move(TILE_SIZE, 0)
                moves += 1
            if keys[pygame.K_w]:
                player.move(0, -TILE_SIZE)
                moves += 1
            if keys[pygame.K_s]:
                player.move(0, TILE_SIZE)
                moves += 1

            screen.fill(WHITE)
            draw_maze(screen, maze)
            player.draw(screen)
            pygame.draw.rect(screen, GREEN, goal_rect)
            draw_timer(screen, start_time)
            draw_level_counter(screen, level)

            # Handle bombs
            for bomb in bombs:
                if player.rect.colliderect(bomb.rect.inflate(2 * TILE_SIZE, 2 * TILE_SIZE)):
                    bomb.start_countdown()
                if bomb.is_exploded():
                    bombs.remove(bomb)
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            bx = bomb.rect.x // TILE_SIZE + dx
                            by = bomb.rect.y // TILE_SIZE + dy
                            if 0 <= bx < len(maze[0]) and 0 <= by < len(maze):
                                maze[by][bx] = 0

            for bomb in bombs:
                bomb.draw(screen)

            if player.rect.colliderect(goal_rect):
                if not show_success_message:
                    end_time = time.time()
                    performance_metrics.append({
                        'time': end_time - start_time,
                        'moves': moves
                    })
                    print("You reached the goal!")
                    show_success_message = True
                    success_message_start_time = time.time()

            if show_success_message:
                draw_success_message(screen)
                if time.time() - success_message_start_time > 2:
                    show_success_message = False
                    running = False
                    level += 1

            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    main()
