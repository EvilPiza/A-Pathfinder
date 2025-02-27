import pygame
import math
import heapq
import random

WIDTH, HEIGHT = 800, 600
HEX_SIZE = 30
ROWS = int(HEIGHT // HEX_SIZE)
COLS = int(WIDTH // (HEX_SIZE * 1.5))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hexagonal Pathfinding")

grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
start = None
goal = None
path = []

HEX_DIRECTIONS = [
    (+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)
]

def axial_to_pixel(q, r):
    x = HEX_SIZE * 3/2 * q
    y = HEX_SIZE * math.sqrt(3) * (r + q / 2)
    return int(x + WIDTH // 2), int(y + HEIGHT // 2)

def pixel_to_axial(x, y):
    q = (2/3 * x) / HEX_SIZE
    r = (-1/3 * x + math.sqrt(3)/3 * y) / HEX_SIZE
    return round(q), round(r)

def draw_hex(q, r, color):
    cx, cy = axial_to_pixel(q, r)
    points = []
    for i in range(6):
        angle = math.radians(60 * i)
        px = cx + HEX_SIZE * math.cos(angle)
        py = cy + HEX_SIZE * math.sin(angle)
        points.append((px, py))
    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, GRAY, points, 2)

def draw_grid():
    for q in range(-COLS // 2, COLS // 2):
        for r in range(-ROWS // 2, ROWS // 2):
            color = WHITE if grid[r + ROWS // 2][q + COLS // 2] == 0 else BLACK
            if (q, r) == start:
                color = BLUE
            elif (q, r) == goal:
                color = RED
            elif (q, r) in path:
                color = GREEN
            draw_hex(q, r, color)

def heuristic(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[0] + a[1] - b[0] - b[1])) // 2

def a_star(start, goal, temperature=10.0):
    # From what I've tested, 10 is best
    global path
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while queue:
        _, current = heapq.heappop(queue)

        if current == goal:
            break

        neighbors = []
        for dq, dr in HEX_DIRECTIONS:
            neighbor = (current[0] + dq, current[1] + dr)

            if -COLS // 2 <= neighbor[0] < COLS // 2 and -ROWS // 2 <= neighbor[1] < ROWS // 2:
                row, col = neighbor[1] + ROWS // 2, neighbor[0] + COLS // 2
                if grid[row][col] == 0:
                    neighbors.append(neighbor)
        
        random.shuffle(neighbors)

        for neighbor in neighbors:
            new_cost = cost_so_far[current] + 1

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                
                noise = random.uniform(0, temperature)  # More randomness with higher temperature
                priority = new_cost + heuristic(goal, neighbor) + noise
                
                heapq.heappush(queue, (priority, neighbor))
                came_from[neighbor] = current

    path = []
    if goal in came_from:
        temp = goal
        while temp:
            path.append(temp)
            temp = came_from[temp]
        path.reverse()

running = True
while running:
    screen.fill(WHITE)
    draw_grid()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Detect left click to set the start point
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            q, r = pixel_to_axial(pos[0] - WIDTH // 2, pos[1] - HEIGHT // 2)
            start = (q, r)

        # Detect mouse movement to update goal dynamically
        if start is not None:
            pos = pygame.mouse.get_pos()
            q, r = pixel_to_axial(pos[0] - WIDTH // 2, pos[1] - HEIGHT // 2)
            goal = (q, r)
            if goal != start:
                a_star(start, goal)

        if pygame.mouse.get_pressed()[2]:  # Right Click
            pos = pygame.mouse.get_pos()
            q, r = pixel_to_axial(pos[0] - WIDTH // 2, pos[1] - HEIGHT // 2)
            
            row, col = r + ROWS // 2, q + COLS // 2
            if 0 <= row < ROWS and 0 <= col < COLS:
                grid[row][col] = 1 - grid[row][col]
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Reset
                grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                start = None
                goal = None
                path = []

pygame.quit()
