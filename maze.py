import pygame
import random
import sys
from collections import deque

BG = (12, 14, 23)
WALL = (210, 215, 235)
CELL_UNVIS = (20, 23, 36)
CELL_VIS = (30, 35, 55)
MOUSE_COL = (255, 200, 50)
FRONTIER = (45, 85, 195)
PATH_COL = (45, 215, 100)
START_COL = (35, 200, 80)
END_COL = (225, 55, 55)

WIN_W, WIN_H = 512, 512

ROWS = 12
COLS = 12

# ms per animation step for each phase
GEN_DELAY = 12
SOLVE_DELAY = 6


class Maze:
    DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, rows, cols):
        self.R = rows
        self.C = cols
        self.northWall = [[1] * cols for _ in range(rows + 1)]
        self.eastWall = [[1] * (cols + 1) for _ in range(rows)]
        self.start = None
        self.end = None

    def remove_wall(self, r1, c1, r2, c2):
        dr, dc = r2 - r1, c2 - c1
        if dr == -1:
            self.northWall[r1][c1] = 0
        elif dr == 1:
            self.northWall[r2][c2] = 0
        elif dc == 1:
            self.eastWall[r1][c2] = 0
        elif dc == -1:
            self.eastWall[r1][c1] = 0

    def can_move(self, r, c, dr, dc):
        nr, nc = r + dr, c + dc
        if not (0 <= nr < self.R and 0 <= nc < self.C):
            return False
        if dr == -1:
            return self.northWall[r][c] == 0
        if dr == 1:
            return self.northWall[nr][nc] == 0
        if dc == 1:
            return self.eastWall[r][nc] == 0
        if dc == -1:
            return self.eastWall[r][c] == 0

    def neighbors(self, r, c):
        return [(r + dr, c + dc) for dr, dc in self.DIRS if self.can_move(r, c, dr, dc)]


def gen_steps(maze):
    R, C = maze.R, maze.C
    visited = [[False] * C for _ in range(R)]
    dirs = list(maze.DIRS)
    sr, sc = random.randrange(R), random.randrange(C)
    visited[sr][sc] = True
    stack = [(sr, sc)]
    yield ("step", sr, sc, frozenset(stack))
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
            yield ("step", nr, nc, frozenset(stack))
        else:
            stack.pop()
            if stack:
                yield ("step", stack[-1][0], stack[-1][1], frozenset(stack))
    yield ("done",)


def solve_steps(maze):
    sr, sc = maze.start
    er, ec = maze.end
    R, C = maze.R, maze.C
    visited = [[False] * C for _ in range(R)]
    came_from = [[None] * C for _ in range(R)]
    q = deque([(sr, sc)])
    visited[sr][sc] = True
    while q:
        r, c = q.popleft()
        yield ("visit", r, c)
        if r == er and c == ec:
            path, cur = [], (er, ec)
            while cur:
                path.append(cur)
                cur = came_from[cur[0]][cur[1]]
            yield ("path", list(reversed(path)))
            return
        for nr, nc in maze.neighbors(r, c):
            if not visited[nr][nc]:
                visited[nr][nc] = True
                came_from[nr][nc] = (r, c)
                q.append((nr, nc))


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

        self.frontier = set()
        self.path_set = set()
        self.mouse = None

    def cell_rect(self, r, c):
        cs = self.cs
        x = self.ox + c * cs
        y = self.oy + (self.maze.R - 1 - r) * cs
        return pygame.Rect(x, y, cs, cs)

    def cell_color(self, r, c, phase):
        if phase == "generating":
            if self.mouse == (r, c):
                return MOUSE_COL
            return CELL_UNVIS
        if phase in ("solving", "solved"):
            if (r, c) in self.path_set:
                return PATH_COL
            if (r, c) in self.frontier:
                return FRONTIER
            return CELL_UNVIS
        return CELL_UNVIS

    def draw_all(self, phase):
        maze = self.maze
        R, C, cs = maze.R, maze.C, self.cs
        surf = self.surf
        surf.fill(BG)
        wt = max(1, cs // 10)  # wall thickness scales with cell size

        for r in range(R):
            for c in range(C):
                rect = self.cell_rect(r, c)
                pygame.draw.rect(surf, self.cell_color(r, c, phase), rect)

                x, y = rect.x, rect.y
                if maze.northWall[r + 1][c]:
                    pygame.draw.rect(surf, WALL, (x, y, cs + wt, wt))
                if maze.northWall[r][c]:
                    pygame.draw.rect(surf, WALL, (x, y + cs, cs + wt, wt))
                if maze.eastWall[r][c]:
                    pygame.draw.rect(surf, WALL, (x, y, wt, cs + wt))
                if maze.eastWall[r][c + 1]:
                    pygame.draw.rect(surf, WALL, (x + cs, y, wt, cs + wt))

        if maze.start:
            self._marker(*maze.start, START_COL, "S")
        if maze.end:
            self._marker(*maze.end, END_COL, "E")

    def redraw_cell(self, r, c, phase):
        maze = self.maze
        cs = self.cs
        wt = max(1, cs // 10)
        rect = self.cell_rect(r, c)
        x, y = rect.x, rect.y
        surf = self.surf

        pygame.draw.rect(surf, self.cell_color(r, c, phase), rect)
        if maze.northWall[r + 1][c]:
            pygame.draw.rect(surf, WALL, (x, y, cs + wt, wt))
        else:
            pygame.draw.rect(surf, self.cell_color(r, c, phase), (x, y, cs, wt))
        if maze.northWall[r][c]:
            pygame.draw.rect(surf, WALL, (x, y + cs, cs + wt, wt))
        if maze.eastWall[r][c]:
            pygame.draw.rect(surf, WALL, (x, y, wt, cs + wt))
        if maze.eastWall[r][c + 1]:
            pygame.draw.rect(surf, WALL, (x + cs, y, wt, cs + wt))

        if maze.start == (r, c):
            self._marker(r, c, START_COL, "S")
        if maze.end == (r, c):
            self._marker(r, c, END_COL, "E")

    def _marker(self, r, c, color, letter):
        rect = self.cell_rect(r, c)
        cs = self.cs
        pad = max(2, cs // 6)
        inner = rect.inflate(-pad * 2, -pad * 2)
        pygame.draw.rect(self.surf, color, inner, border_radius=max(2, cs // 5))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Maze Generator & Solver")
    clock = pygame.time.Clock()

    def pump():
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_q, pygame.K_ESCAPE):
                return False
        return True

    def pause(ms):
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < ms:
            if not pump():
                return False
            clock.tick(60)
        return True

    def shutdown():
        pygame.quit()
        sys.exit()

    random.seed()

    maze = Maze(ROWS, COLS)
    view = View(screen, maze)
    view.draw_all("grid")
    pygame.display.flip()
    if not pause(200):
        shutdown()

    # Generating the maze
    it = gen_steps(maze)
    phase = "generating"
    last_t = pygame.time.get_ticks()

    while True:
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
                _, r, c, stk = step
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

    # fixed start/end
    # coordinates are drawn with inverted Y, so flip rows for visual corners
    maze.start = (ROWS - 1, 0)
    maze.end = (0, COLS - 1)

    view.draw_all("gen_done")
    pygame.display.flip()
    if not pause(200):
        shutdown()

    # Solving the maze
    it = solve_steps(maze)
    phase = "solving"
    last_t = pygame.time.get_ticks()

    while True:
        if not pump():
            shutdown()
        now = pygame.time.get_ticks()
        if now - last_t >= SOLVE_DELAY:
            last_t = now
            try:
                step = next(it)
            except StopIteration:
                break

            k = step[0]
            if k == "visit":
                _, r, c = step
                view.frontier.add((r, c))
                view.redraw_cell(r, c, phase)
            elif k == "path":
                _, path = step
                view.path_set = set(path)
                phase = "solved"
                view.draw_all("solved")
                break

        pygame.display.flip()
        clock.tick(120)

    pygame.display.flip()
    if not pause(1000):
        shutdown()

    pygame.quit()
    sys.exit()


main()
