import pygame
import random
import sys

pygame.init()

# Constant Variables
WIDTH, HEIGHT = 300, 500
FPS = 30  # Slower frame rate for slower gameplay
CELL = 20
ROWS = (HEIGHT - 120) // CELL
COLS = WIDTH // CELL

# Game Settings
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
clock = pygame.time.Clock()
pygame.display.set_caption("Pytris")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (31, 25, 76)
GRID = (31, 25, 132)
LOSE = (255, 0, 0)  # Color for game over popup

# Load Assets
ASSETS = {}
try:
    ASSETS = {
        1: pygame.image.load("1.png"),
        2: pygame.image.load("2.png"),
        3: pygame.image.load("3.png"),
        4: pygame.image.load("4.png"),
    }
except pygame.error as e:
    print("Error loading assets. Using placeholder blocks:", e)

# Fonts Initialization
font = pygame.font.SysFont("verdana", 20)
font2 = pygame.font.SysFont("verdana", 20)

# Shape Class
class Shape:
    VERSION = {
        'I': [[1, 5, 9, 13], [4, 5, 6, 7]],
        'Z': [[1, 2, 5, 6], [0, 4, 5, 9]],
        'S': [[6, 7, 9, 10], [1, 5, 6, 10]],
        'L': [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        'J': [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        'T': [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        'O': [[1, 2, 5, 6]]
    }
    SHAPES = ['I', 'Z', 'S', 'L', 'J', 'T', 'O']

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(self.SHAPES)
        self.shape = self.VERSION[self.type]
        self.color = random.randint(1, 4)
        self.orientation = 0

    def image(self):
        return self.shape[self.orientation]

    def rotate(self):
        self.orientation = (self.orientation + 1) % len(self.shape)

# Game Class
class Pytris:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.score = 0
        self.level = 1
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.next = None
        self.end = False
        self.new_shape()

    def make_grid(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] > 0:
                    x = j * CELL
                    y = i * CELL
                    shape = ASSETS.get(self.grid[i][j], pygame.Surface((CELL, CELL)))
                    if not ASSETS.get(self.grid[i][j]):
                        shape.fill(WHITE)
                    SCREEN.blit(shape, (x, y))
                    pygame.draw.rect(SCREEN, BLACK, (x, y, CELL, CELL), 1)

        for i in range(self.rows + 1):
            pygame.draw.line(SCREEN, GRID, (0, i * CELL), (WIDTH, i * CELL))
        for j in range(self.cols + 1):
            pygame.draw.line(SCREEN, GRID, (j * CELL, 0), (j * CELL, HEIGHT - 120))

    def new_shape(self):
        if not self.next:
            self.next = Shape(5, 0)
        self.figure = self.next
        self.next = Shape(5, 0)
        if self.collision():
            self.end = True
            
    def collision(self):
        for i in range(4):
            for j in range(4):
                if (i * 4 + j) in self.figure.image():
                    block_row = i + self.figure.y
                    block_col = j + self.figure.x
                    if (block_row >= self.rows or block_col >= self.cols or block_col < 0 or self.grid[block_row][block_col] > 0):
                        return True
        return False
    
    def remove_row(self):
        rerun = False

        for y in range(self.rows-1, 0, -1):
            completed = True

            for x in range(0, self.cols):
                if self.grid[y][x]== 0:
                    completed = False

            if completed:
                del self.grid[y]
                self.grid.insert(0, [0 for i in range(self.cols)])
                self.score += 100
                if self.score % 10 == 0:
                    self.level += 1
                rerun = True

        if rerun:
            self.remove_row()

    def lock_shape(self):
        for i in range(4):
            for j in range(4):
                if (i * 4 + j) in self.figure.image():
                    block_row = i + self.figure.y
                    block_col = j + self.figure.x
                    if 0 <= block_row < self.rows and 0 <= block_col < self.cols:
                        self.grid[block_row][block_col] = self.figure.color
        self.new_shape()
        self.remove_row()

    def move_down(self):
        self.figure.y += 1
        if self.collision():
            self.figure.y -= 1
            self.lock_shape()

    def move_left(self):
        self.figure.x -= 1
        if self.collision():
            self.figure.x += 1

    def move_right(self):
        self.figure.x += 1
        if self.collision():
            self.figure.x -= 1

    def freefall(self):
        while not self.collision():
            self.figure.y += 1
        self.figure.y -= 1
        self.lock_shape()

    def rotate(self):
        prev_orientation = self.figure.orientation
        self.figure.rotate()
        if self.collision():
            self.figure.orientation = prev_orientation

    def end_game(self):
        popup = pygame.Rect(50, 140, WIDTH-100, HEIGHT-350)
        pygame.draw.rect(SCREEN, BLACK, popup)
        pygame.draw.rect(SCREEN, LOSE, popup, 2)

        game_over = font2.render("Game Over", True, WHITE)
        option1 = font2.render("Press r to restart", True, LOSE)
        option2 = font2.render("Press q to quit", True, LOSE)

        SCREEN.blit(game_over, (popup.centerx - game_over.get_width() // 2, popup.y + 20))
        SCREEN.blit(option1, (popup.centerx - option1.get_width() // 2, popup.y + 80))
        SCREEN.blit(option2, (popup.centerx - option2.get_width() // 2, popup.y + 110))

# Main Game Loop
def main():
    pytris = Pytris(ROWS, COLS)
    counter = 0
    space_pressed = False
    run = True

    while run:
        SCREEN.fill(BG_COLOR)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not pytris.end:
                    if event.key == pygame.K_LEFT:
                        pytris.move_left()
                    elif event.key == pygame.K_RIGHT:
                        pytris.move_right()
                    elif event.key == pygame.K_DOWN:
                        pytris.move_down()
                    elif event.key == pygame.K_UP:
                        pytris.rotate()
                    elif event.key == pygame.K_SPACE:
                        space_pressed = True
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    run = False
                # Restart the game
                if event.key == pygame.K_r and pytris.end:
                    pytris = Pytris(ROWS, COLS)

        # Handle Space Key for Freefall
        if space_pressed:
            pytris.freefall()
            space_pressed = False

        # Automatic Downward Movement
        if counter % (FPS // (pytris.level + 1)) == 0:
            if not pytris.end:
                pytris.move_down()

        # Draw the Game Grid and Current Shape
        pytris.make_grid()
        for block in pytris.figure.image():
            i = block // 4
            j = block % 4
            x = CELL * (pytris.figure.x + j)
            y = CELL * (pytris.figure.y + i)
            shape = ASSETS.get(pytris.figure.color, pygame.Surface((CELL, CELL)))
            if not ASSETS.get(pytris.figure.color):
                shape.fill(WHITE)
            SCREEN.blit(shape, (x, y))
            pygame.draw.rect(SCREEN, BLACK, (x, y, CELL, CELL), 1)

        # Control Panel for Next Block
        if pytris.next:
            for i in range(4):
                for j in range(4):
                    if (i * 4 + j) in pytris.next.image():
                        x = CELL * (pytris.next.x + j - 4)
                        y = HEIGHT - 100 + CELL * i
                        image = ASSETS.get(pytris.next.color, pygame.Surface((CELL, CELL)))
                        if not ASSETS.get(pytris.next.color):
                            image.fill(WHITE)
                        SCREEN.blit(image, (x, y))

        if pytris.end:
            # Display the Game Over screen
            pytris.end_game()

        # Render and Display Score & Level
        score_text = font2.render(f"Score: {pytris.score}", True, WHITE)
        level_text = font2.render(f"Level: {pytris.level}", True, WHITE)
        SCREEN.blit(score_text, (250-score_text.get_width()//2, HEIGHT-100))
        SCREEN.blit(level_text, (250-level_text.get_width()//2, HEIGHT-55)) 

        pygame.display.update()
        counter += 1
        clock.tick(FPS)

if __name__ == "__main__":
    main()