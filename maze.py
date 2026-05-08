import pygame
import random
import sys

BG = (12, 14, 23)
WALL = (210, 215, 235)
CELL_UNVIS = (20, 23, 36)
MOUSE_COL = (255, 200, 50)

WIN_W, WIN_H = 512, 512

ROWS = 12
COLS = 12

GEN_DELAY = 12  # ms per carve step


class Maze:
    DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, rows, cols):
        self.R = rows
        self.C = cols
        self.northWall = [[1] * cols for _ in range(rows + 1)]
        self.eastWall = [[1] * (cols + 1) for _ in range(rows)]

    def remove_wall(self, r1, c1, r2, c2):
        # Open the shared wall between two adjacent cells.
        dr, dc = r2 - r1, c2 - c1
        if dr == -1:
            self.northWall[r1][c1] = 0
        elif dr == 1:
            self.northWall[r2][c2] = 0
        elif dc == 1:
            self.eastWall[r1][c2] = 0
        elif dc == -1:
            self.eastWall[r1][c1] = 0


def gen_steps(maze):
    # Stack-based DFS "mouse" that yields animation steps.
    R, C = maze.R, maze.C
    visited = [[False] * C for _ in range(R)]
    dirs = list(maze.DIRS)
    sr, sc = random.randrange(R), random.randrange(C)
    visited[sr][sc] = True
    stack = [(sr, sc)]
    yield ("step", sr, sc)
    while stack:
        r, c = stack[-1]
        nbrs = [
            (r + dr, c + dc, dr, dc)
            for dr, dc in dirs
            if 0 <= r + dr < R and 0 <= c + dc < C and not visited[r + dr][c + dc]
        ]
        if nbrs:
            nr, nc, dr, dc = random.choice(nbrs)
            maze.remove_wall(r, c, nr, nc)
            visited[nr][nc] = True
            stack.append((nr, nc))
            yield ("step", nr, nc)
        else:
            stack.pop()
            if stack:
                yield ("step", stack[-1][0], stack[-1][1])
    yield ("done",)


class View:
    def __init__(self, surf, maze):
        self.surf = surf
        self.maze = maze
        R, C = maze.R, maze.C
        avail_w = WIN_W - 40
        avail_h = WIN_H - 40
        self.cs = max(8, min(avail_w // C, avail_h // R))
        self.ox = (WIN_W - C * self.cs) // 2
        self.oy = (WIN_H - R * self.cs) // 2
        self.mouse = None

    def cell_rect(self, r, c):
        cs = self.cs
        x = self.ox + c * cs
        y = self.oy + (self.maze.R - 1 - r) * cs
        return pygame.Rect(x, y, cs, cs)

    def draw_all(self, phase):
        # Draw grid and walls; only the mouse is highlighted.
        maze = self.maze
        R, C, cs = maze.R, maze.C, self.cs
        surf = self.surf
        surf.fill(BG)
        wt = max(1, cs // 10)

        for r in range(R):
            for c in range(C):
                rect = self.cell_rect(r, c)
                color = (
                    MOUSE_COL
                    if self.mouse == (r, c) and phase == "generating"
                    else CELL_UNVIS
                )
                pygame.draw.rect(surf, color, rect)

                x, y = rect.x, rect.y
                if maze.northWall[r + 1][c]:
                    pygame.draw.rect(surf, WALL, (x, y, cs + wt, wt))
                if maze.northWall[r][c]:
                    pygame.draw.rect(surf, WALL, (x, y + cs, cs + wt, wt))
                if maze.eastWall[r][c]:
                    pygame.draw.rect(surf, WALL, (x, y, wt, cs + wt))
                if maze.eastWall[r][c + 1]:
                    pygame.draw.rect(surf, WALL, (x + cs, y, wt, cs + wt))

    def redraw_cell(self, r, c, phase):
        maze = self.maze
        cs = self.cs
        wt = max(1, cs // 10)
        rect = self.cell_rect(r, c)
        x, y = rect.x, rect.y
        surf = self.surf

        color = (
            MOUSE_COL if self.mouse == (r, c) and phase == "generating" else CELL_UNVIS
        )
        pygame.draw.rect(surf, color, rect)
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
    pygame.display.set_caption("Maze Generation")
    clock = pygame.time.Clock()

    def pump():
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_q, pygame.K_ESCAPE):
                return False
        return True

    def shutdown():
        pygame.quit()
        sys.exit()

    random.seed()

    maze = Maze(ROWS, COLS)
    view = View(screen, maze)
    view.draw_all("grid")
    pygame.display.flip()

    it = gen_steps(maze)
    phase = "generating"
    last_t = pygame.time.get_ticks()

    while True:
        # Step the generator on a timer and repaint just changed cells.
        if not pump():
            shutdown()
        now = pygame.time.get_ticks()
        if now - last_t >= GEN_DELAY:
            last_t = now
            try:
                step = next(it)
            except StopIteration:
                break

            k = step[0]
            if k == "step":
                _, r, c = step
                old = view.mouse
                view.mouse = (r, c)
                if old and old != (r, c):
                    view.redraw_cell(*old, phase)
                view.redraw_cell(r, c, phase)
            elif k == "done":
                view.mouse = None
                break

        pygame.display.flip()
        clock.tick(120)

    pygame.display.flip()
    pygame.time.wait(400)
    shutdown()


if __name__ == "__main__":
    main()
