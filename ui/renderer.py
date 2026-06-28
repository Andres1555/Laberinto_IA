import math
import os
import pygame
from typing import Tuple, List

from config.colors import Colors


class MazeRenderer:
    def __init__(self, screen: pygame.Surface, font_key: pygame.font.Font, font_info: pygame.font.Font):
        self.screen = screen
        self.font_key = font_key
        self.font_info = font_info
        self._load_sprites()

    def _load_sprites(self):
        base = os.path.join(os.path.dirname(__file__), "..", "sprites")
        self.tex_floor = pygame.image.load(os.path.join(base, "Celdaverdes.png"))
        self.tex_wall  = pygame.image.load(os.path.join(base, "cerldas_de_cierre.png"))
        self.tex_start = pygame.image.load(os.path.join(base, "bombermansalida.png"))
        self.tex_goal  = pygame.image.load(os.path.join(base, "bombermanentrada.png"))

    @staticmethod
    def _rounded_rect(surface, color, rect, radius=6):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    @staticmethod
    def _glow(surface, color_rgba, center, radius):
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            a = int(color_rgba[3] * (r / radius) * 0.5)
            pygame.draw.circle(s, (*color_rgba[:3], a), (radius, radius), r)
        surface.blit(s, (center[0] - radius, center[1] - radius))

    def draw(self, grid, rows, cols, ox, oy,
             agent, start, goal, glow_phase, path_idx, cell_size=55):
        self.cs = cell_size
        self._draw_grid(grid, rows, cols, ox, oy)
        self._draw_frame(ox, oy, cols, rows)
        self._draw_closed(agent, start, goal, ox, oy, rows, cols)
        self._draw_open(agent, start, goal, ox, oy, glow_phase)
        self._draw_neighbors(agent.neighbors_being_checked, ox, oy)
        self._draw_current(agent.current_node, agent.finished, ox, oy)
        if agent.path_found and agent.optimal_path:
            self._draw_path(agent, start, goal, ox, oy, glow_phase, path_idx)
        self._draw_start(start, ox, oy, glow_phase)
        self._draw_goal(goal, ox, oy, glow_phase)

    # ── Grid ──
    def _draw_grid(self, grid, rows, cols, ox, oy):
        cs = self.cs
        for r in range(rows):
            for c in range(cols):
                x = ox + c * cs
                y = oy + r * cs
                if grid[r][c] == 1:
                    tex = pygame.transform.scale(self.tex_wall, (cs, cs))
                    self.screen.blit(tex, (x, y))
                else:
                    tex = pygame.transform.scale(self.tex_floor, (cs, cs))
                    self.screen.blit(tex, (x, y))

    def _draw_frame(self, ox, oy, cols, rows):
        fw = cols * self.cs
        fh = rows * self.cs
        for i in range(6, 0, -1):
            a = 30 - i * 4
            cl = (45 + i * 3, 55 + i * 3, 130 + i * 5, a)
            pygame.draw.rect(self.screen, cl[:3], (ox - i - 2, oy - i - 2, fw + i * 2 + 4, fh + i * 2 + 4), 1)
        pygame.draw.rect(self.screen, (60, 70, 160), (ox - 3, oy - 3, fw + 6, fh + 6), 2)

    # ── Cell info (f arriba, g abajo-izq, h abajo-der) ──
    def _cell_info(self, pos, agent, ox, oy):
        if pos not in agent.came_from:
            return
        node = agent.came_from[pos]
        r, c = pos
        x = ox + c * self.cs
        y = oy + r * self.cs

        sf = self.font_key.render(f"f{node.f:.0f}", True, (0, 0, 0))
        sg = self.font_info.render(f"g{node.g:.0f}", True, (0, 0, 0))
        sh = self.font_info.render(f"h{node.h:.0f}", True, (0, 0, 0))

        self.screen.blit(sf, (x + 5, y + 4))
        self.screen.blit(sg, (x + 4, y + self.cs - sg.get_height() - 4))
        self.screen.blit(sh, (x + self.cs - sh.get_width() - 4, y + self.cs - sh.get_height() - 4))

    # ── Closed ──
    def _draw_closed(self, agent, start, goal, ox, oy, rows, cols):
        cs = agent.closed_set
        if not cs:
            return
        md = rows + cols
        for pos in cs:
            if pos == start or pos == goal:
                continue
            r, c = pos
            x = ox + c * self.cs
            y = oy + r * self.cs
            rect = pygame.Rect(x + 2, y + 2, self.cs - 4, self.cs - 4)
            t = min(1.0, (abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])) / md)
            cl = (
                int(Colors.CLOSED_SET[0] + (Colors.CLOSED_SET_LIGHT[0] - Colors.CLOSED_SET[0]) * (1 - t)),
                int(Colors.CLOSED_SET[1] + (Colors.CLOSED_SET_LIGHT[1] - Colors.CLOSED_SET[1]) * (1 - t)),
                int(Colors.CLOSED_SET[2] + (Colors.CLOSED_SET_LIGHT[2] - Colors.CLOSED_SET[2]) * (1 - t)),
            )
            self._rounded_rect(self.screen, cl, rect, 5)
            self._cell_info(pos, agent, ox, oy)

    # ── Open ──
    def _draw_open(self, agent, start, goal, ox, oy, gp):
        os = agent.open_set
        if not os:
            return
        for pos in os:
            if pos == start or pos == goal:
                continue
            r, c = pos
            x = ox + c * self.cs
            y = oy + r * self.cs
            rect = pygame.Rect(x + 2, y + 2, self.cs - 4, self.cs - 4)
            p = int(18 * math.sin(gp * 3 + r + c))
            cl = (
                min(255, Colors.OPEN_SET[0] + p),
                min(255, Colors.OPEN_SET[1] + p),
                min(255, Colors.OPEN_SET[2] + p),
            )
            self._rounded_rect(self.screen, cl, rect, 5)
            self._cell_info(pos, agent, ox, oy)

    # ── Neighbors ──
    def _draw_neighbors(self, neighbors, ox, oy):
        for pos in neighbors:
            r, c = pos
            x = ox + c * self.cs
            y = oy + r * self.cs
            rect = pygame.Rect(x + 1, y + 1, self.cs - 2, self.cs - 2)
            pygame.draw.rect(self.screen, Colors.NEIGHBOR_CHECK, rect, 2, border_radius=5)

    # ── Current ──
    def _draw_current(self, node, finished, ox, oy):
        if node is None or finished:
            return
        r, c = node.position
        x = ox + c * self.cs
        y = oy + r * self.cs
        cx = x + self.cs // 2
        cy = y + self.cs // 2
        self._glow(self.screen, (*Colors.CURRENT, 100), (cx, cy), self.cs)
        rect = pygame.Rect(x + 2, y + 2, self.cs - 4, self.cs - 4)
        self._rounded_rect(self.screen, Colors.CURRENT, rect, 6)

    # ── Path ──
    def _draw_path(self, agent, start, goal, ox, oy, gp, idx):
        path = agent.optimal_path
        n = min(idx, len(path))
        for i in range(n):
            pos = path[i]
            if pos == start or pos == goal:
                continue
            r, c = pos
            x = ox + c * self.cs
            y = oy + r * self.cs
            wv = math.sin(gp * 2 - i * 0.3) * 0.25 + 0.75
            cl = (int(Colors.OPTIMAL_PATH[0] * wv), int(Colors.OPTIMAL_PATH[1] * wv), int(Colors.OPTIMAL_PATH[2] * wv))
            rect = pygame.Rect(x + 3, y + 3, self.cs - 6, self.cs - 6)
            self._rounded_rect(self.screen, cl, rect, 6)
            self._cell_info(pos, agent, ox, oy)

    # ── Start / Goal ──
    def _draw_start(self, start, ox, oy, gp):
        sr, sc = start
        sx = ox + sc * self.cs
        sy = oy + sr * self.cs
        cx = sx + self.cs // 2
        cy = sy + self.cs // 2
        gs = int(self.cs * (1.2 + 0.2 * math.sin(gp * 2)))
        self._glow(self.screen, (*Colors.START, 90), (cx, cy), gs)
        tex = pygame.transform.scale(self.tex_start, (self.cs, self.cs))
        self.screen.blit(tex, (sx, sy))

    def _draw_goal(self, goal, ox, oy, gp):
        gr, gc = goal
        gx = ox + gc * self.cs
        gy = oy + gr * self.cs
        cx = gx + self.cs // 2
        cy = gy + self.cs // 2
        gs = int(self.cs * (1.3 + 0.25 * math.sin(gp * 2.5)))
        self._glow(self.screen, (*Colors.GOAL, 100), (cx, cy), gs)
        tex = pygame.transform.scale(self.tex_goal, (self.cs, self.cs))
        self.screen.blit(tex, (gx, gy))
