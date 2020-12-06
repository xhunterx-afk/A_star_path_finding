import pygame
import sys
from queue import PriorityQueue

# Screen/Display settings
Width = 800
Display = pygame.display.set_mode((Width, Width))
pygame.display.set_caption("A* Path Finding")

# Colors
Red = (255, 0, 0)
Black = (0, 0, 0)
White = (255, 255, 255)
Green = (0, 128, 0)
Orange = (255, 165, 0)
Purple = (128, 0, 128)
Grey = (128, 128, 128)

Turquoise = (64, 224, 208)


# defining rows and cols and returning for every function a color
class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = White
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_post(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == Red

    def is_open(self):
        return self.color == Green

    def is_barrier(self):
        return self.color == Black

    def is_start(self):
        return self.color == Orange

    def is_end(self):
        return self.color == Turquoise

    def reset(self):
        self.color = White

    def make_start(self):
        self.color = Orange

    def make_close(self):
        self.color = Red

    def make_open(self):
        self.color = Green

    def make_barrier(self):
        self.color = Black

    def make_end(self):
        self.color = Turquoise

    def make_path(self):
        self.color = Purple

    def draw(self, display):
        pygame.draw.rect(Display, self.color, (self.x, self.y, self.width, self.width))

    # defining the movement
    def update_neighbors(self, grid):
        self.neighbors = []

        # Going Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        # Going Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        # Going Right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        # Going Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


# Defining heretic
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


# draw a path
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


# defining the algorithm of the a*
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}  # inf stand for infinite
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}  # inf stand for infinite
    f_score[start] = h(start.get_post(), end.get_post())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        current = open_set.get()[2]
        print(type(current))
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_post(), end.get_post())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_close()

    return False


# Making a grid
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Node(i, j, gap, rows)
            grid[i].append(spot)
    return grid


# Drawing a line for a for the rows
def draw_grid(display, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(display, Grey, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(display, Grey, (j * gap, 0), (j * gap, width))


# draw a cube
def draw(display, grid, rows, width):
    display.fill(White)

    for row in grid:
        for spot in row:
            spot.draw(display)

    draw_grid(display, rows, width)
    pygame.display.update()


# getting the position
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    rows = y // gap
    col = x // gap

    return rows, col


# noinspection PyUnresolvedReferences
def main(display, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    while True:
        draw(display, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Left mouse click
            elif pygame.mouse.get_pressed(3)[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]

                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            # Right mouse click
            elif pygame.mouse.get_pressed(5)[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()

                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(display, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_r:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)



main(Display, Width)
