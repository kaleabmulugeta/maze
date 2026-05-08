import pygame
import sys

BG = (12, 14, 23)
WALL = (210, 215, 235)
CELL_UNVIS = (20, 23, 36)

WIN_W, WIN_H = 512, 512

ROWS = 12
COLS = 12


class Maze:
    def __init__(self, rows, cols):
        self.R = rows
        self.C = cols
        # Wall arrays start as fully closed grid.
        self.northWall = [[1] * cols for _ in range(rows + 1)]
        self.eastWall = [[1] * (cols + 1) for _ in range(rows)]


class View:
    def __init__(self, surf, maze):
        self.surf = surf
        self.maze = maze
        R, C = maze.R, maze.C
        avail_w = WIN_W - 40
        avail_h = WIN_H - 40
        # Compute cell size and center the grid.
        self.cs = max(8, min(avail_w // C, avail_h // R))
        self.ox = (WIN_W - C * self.cs) // 2
        self.oy = (WIN_H - R * self.cs) // 2

    def cell_rect(self, r, c):
        cs = self.cs
        x = self.ox + c * cs
        y = self.oy + (self.maze.R - 1 - r) * cs
        return pygame.Rect(x, y, cs, cs)

    def draw_grid(self):
        # Draw empty cells plus all intact walls.
        maze = self.maze
        R, C, cs = maze.R, maze.C, self.cs
        surf = self.surf
        surf.fill(BG)
        wt = max(1, cs // 10)

        for r in range(R):
            for c in range(C):
                rect = self.cell_rect(r, c)
                pygame.draw.rect(surf, CELL_UNVIS, rect)

                x, y = rect.x, rect.y
                if maze.northWall[r + 1][c]:
                    pygame.draw.rect(surf, WALL, (x, y, cs + wt, wt))
                if maze.northWall[r][c]:
                    pygame.draw.rect(surf, WALL, (x, y + cs, cs + wt, wt))
                if maze.eastWall[r][c]:
                    pygame.draw.rect(surf, WALL, (x, y, wt, cs + wt))
                if maze.eastWall[r][c + 1]:
                    pygame.draw.rect(surf, WALL, (x + cs, y, wt, cs + wt))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Maze Grid")
    clock = pygame.time.Clock()

    maze = Maze(ROWS, COLS)
    view = View(screen, maze)
    view.draw_grid()
    pygame.display.flip()

    while True:
        # Idle loop until the user quits.
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_q, pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        clock.tick(60)


if __name__ == "__main__":
    main()
