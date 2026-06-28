"""
Aplicación principal — MazeExplorer.
"""

import sys
import pygame

from config.constants import FPS, AppState
from config.colors import Colors
from mazes.definitions import MAZES
from mazes.generator import generate_maze
from agent.astar import AStarAgent
from ui.renderer import MazeRenderer


class TextButton:
    """Botón de texto clickeable (sin recuadro)."""

    def __init__(self, text: str, color, hover_color, action):
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.hovered = False
        self.rect = None

    def draw(self, screen, font, x, y, w=120, h=32):
        color = self.hover_color if self.hovered else self.color
        self.rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (min(255, color[0]+40), min(255, color[1]+40), min(255, color[2]+40)),
                         (x, y, w, 2))
        pygame.draw.rect(screen, (min(255, color[0]+40), min(255, color[1]+40), min(255, color[2]+40)),
                         (x, y, 2, h))
        pygame.draw.rect(screen, (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40)),
                         (x + w - 2, y, 2, h))
        pygame.draw.rect(screen, (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40)),
                         (x, y + h - 2, w, 2))
        surf = font.render(self.text, True, (255, 255, 255))
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if self.rect is None:
            return
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()


class MazeExplorer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Laberinto IA — A* (A-Star)")

        self.speed = 8
        self._step_timer = 0
        self.state = AppState.IDLE
        self.path_animation_index = 0
        self.path_animation_timer = 0
        self.glow_phase = 0.0
        self.fonts = {}
        self.renderer = None
        self.canvas = None
        self.buttons = []
        self.bar_h = 90

        self._init_display()
        self._init_fonts()
        self._init_buttons()
        self._load_maze(1)

    def _init_display(self):
        self.disp_w = 1200
        self.disp_h = 870
        self.screen = pygame.display.set_mode((self.disp_w, self.disp_h))

    def _init_fonts(self):
        try:
            self.fonts = {
                "btn":  pygame.font.SysFont("Segoe UI", 15, bold=True),
                "key":  pygame.font.SysFont("Consolas", 14, bold=True),
                "info": pygame.font.SysFont("Consolas", 12, bold=True),
            }
        except Exception:
            self.fonts = {
                "btn":  pygame.font.Font(None, 19),
                "key":  pygame.font.Font(None, 17),
                "info": pygame.font.Font(None, 13),
            }

    def _init_buttons(self):
        self.buttons = [
            TextButton("ALEATORIO",  (60, 140, 255), (80, 160, 255), self._on_generate),
            TextButton("INICIAR",    (50, 205, 130), (70, 225, 150), self._on_toggle),
            TextButton("REINICIAR",  (200, 120, 50), (220, 140, 70), self._on_reset),
            TextButton("SALIR",      (200, 60, 60),  (220, 80, 80),  self._on_quit),
        ]

    def _on_quit(self):
        pygame.quit()
        sys.exit()

    def _compute_layout(self):
        maze_width = self.cols * self.cell_size
        maze_height = self.rows * self.cell_size
        self.canvas = pygame.Surface((maze_width, maze_height))
        self.maze_offset_x = 0
        self.maze_offset_y = 0
        self.screen_ox = (self.disp_w - maze_width) // 2
        self.screen_oy = (self.disp_h - self.bar_h - maze_height) // 2

    def _load_maze_data(self, maze_data: dict):
        self._current_maze_data = maze_data
        self.maze_name = maze_data["name"]
        raw_grid = maze_data["grid"]
        self.rows = len(raw_grid)
        self.cols = len(raw_grid[0])
        self.cell_size = 65
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        self.start = None
        self.goal = None
        for r in range(self.rows):
            for c in range(self.cols):
                cell = raw_grid[r][c]
                if cell == 'S':
                    self.start = (r, c)
                    self.grid[r][c] = 0
                elif cell == 'G':
                    self.goal = (r, c)
                    self.grid[r][c] = 0
                else:
                    self.grid[r][c] = cell
        self._compute_layout()
        self.renderer = MazeRenderer(self.canvas, self.fonts["key"], self.fonts["info"])
        self.agent = AStarAgent(self.grid, self.start, self.goal)
        self.state = AppState.IDLE
        self.path_animation_index = 0
        self.path_animation_timer = 0
        self._step_timer = 0
        self._update_button_texts()

    def _load_maze(self, maze_id: int):
        self.current_maze_id = maze_id
        self._load_maze_data(MAZES[maze_id])

    def _load_random_maze(self, rows=12, cols=12):
        self.current_maze_id = -1
        self._load_maze_data(generate_maze(rows, cols))

    def _on_generate(self):
        self._load_random_maze()

    def _update_button_texts(self):
        toggle_map = {
            AppState.IDLE: "INICIAR",
            AppState.EXPLORING: "PAUSAR",
            AppState.PAUSED: "REANUDAR",
            AppState.PATH_FOUND: "LISTO",
            AppState.NO_PATH: "SIN RUTA",
        }
        self.buttons[1].text = toggle_map.get(self.state, "INICIAR")

    def _on_toggle(self):
        if self.state == AppState.IDLE:
            self.state = AppState.EXPLORING
        elif self.state == AppState.EXPLORING:
            self.state = AppState.PAUSED
        elif self.state == AppState.PAUSED:
            self.state = AppState.EXPLORING
        self._update_button_texts()

    def _on_reset(self):
        self._load_maze_data(self._current_maze_data)

    # ─────────────────────────────────────────────────────────────────────
    # Eventos
    # ─────────────────────────────────────────────────────────────────────
    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            for btn in self.buttons:
                btn.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif event.key == pygame.K_SPACE:
                    self._on_toggle()

                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    self.speed = min(20, self.speed + 1)

                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.speed = max(1, self.speed - 1)

                elif event.key == pygame.K_r:
                    self._on_reset()

                elif event.key == pygame.K_g:
                    self._on_generate()

                elif event.key == pygame.K_1:
                    self._load_maze(1)
                elif event.key == pygame.K_2:
                    self._load_maze(2)
                elif event.key == pygame.K_3:
                    self._load_maze(3)
                elif event.key == pygame.K_4:
                    self._load_maze(4)

        return True

    # ─────────────────────────────────────────────────────────────────────
    # Game Loop
    # ─────────────────────────────────────────────────────────────────────
    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            running = self._handle_events()

            if self.state == AppState.EXPLORING and not self.agent.finished:
                self._step_timer += 1
                if self._step_timer >= self.speed:
                    self._step_timer = 0
                    done = self.agent.step()
                    if done:
                        self.state = (AppState.PATH_FOUND if self.agent.path_found
                                      else AppState.NO_PATH)
                        self._update_button_texts()

            if self.state == AppState.PATH_FOUND and self.agent.optimal_path:
                self.path_animation_timer += 1
                if self.path_animation_timer % 2 == 0:
                    self.path_animation_index = min(
                        self.path_animation_index + 1,
                        len(self.agent.optimal_path)
                    )

            self.glow_phase += 0.03

            # ── Render ──
            self.screen.fill(Colors.BG_DARK)
            self.canvas.fill(Colors.PATH_FREE)

            self.renderer.draw(
                self.grid, self.rows, self.cols,
                self.maze_offset_x, self.maze_offset_y,
                self.agent, self.start, self.goal,
                self.glow_phase, self.path_animation_index,
                cell_size=self.cell_size
            )

            # Render del canvas 1:1 en pantalla
            self.screen.blit(self.canvas, (self.screen_ox, self.screen_oy))

            # Menu lateral izquierdo (HUD + leyenda + botones)
            mx, my = 10, 12
            mw = 195
            items = []
            bf = self.fonts["btn"]
            lf = self.fonts["info"]

            def add(text, color, font, indent=0, height=18):
                items.append((text, color, font, indent, height))

            add("LABERINTO IA", (100, 200, 255), bf, height=22)
            add(f"Pasos: {self.agent.steps}", (180, 185, 210), lf)

            add("f(n) = g(n) + h(n)", (140, 170, 200), lf)
            if self.agent.path_found:
                add(f"Ruta: {len(self.agent.optimal_path) - 1} pasos", (80, 230, 150), lf)
            add("", None, None, height=6)
            add("── COLORES ──", (160, 180, 220), lf, height=20)
            add("", None, None, height=2)
            add("\u25a0 Rojo   = Buscando", (200, 40, 40), lf, indent=4)
            add("\u25a0 Amarillo = Explorado", (255, 210, 40), lf, indent=4)
            add("\u25a0 Verde  = Ruta \xf3ptima", (0, 240, 150), lf, indent=4)
            add("", None, None, height=4)
            add("── LETRAS ──", (160, 180, 220), lf, height=20)
            add("", None, None, height=2)
            add("f = Costo total", (200, 200, 220), lf, indent=4)
            add("g = Desde inicio", (200, 200, 220), lf, indent=4)
            add("h = Heur\xedstica", (200, 200, 220), lf, indent=4)
            add("", None, None, height=6)

            total_h = sum(h for _, _, _, _, h in items) + 20
            panel = pygame.Surface((mw, total_h))
            panel.fill((22, 42, 30))
            self.screen.blit(panel, (mx, my))
            # Borde pixel art con puntos decorativos en esquinas
            pygame.draw.rect(self.screen, (50, 110, 60), (mx, my, mw, total_h), 2)
            for dx, dy in [(mx+2, my+2), (mx+mw-4, my+2), (mx+2, my+total_h-4), (mx+mw-4, my+total_h-4)]:
                self.screen.set_at((dx, dy), (70, 160, 90))
            cy = my + 8
            for text, color, font, indent, height in items:
                if not text:
                    cy += height
                    continue
                surf = font.render(text, True, color)
                self.screen.blit(surf, (mx + 8 + indent, cy))
                cy += height

            # Barra inferior pixel art
            bar_y = self.disp_h - self.bar_h
            bar = pygame.Surface((self.disp_w, self.bar_h))
            bar.fill((28, 55, 38))
            # Borde superior pixelado (bloques verdes alternando)
            for i in range(0, self.disp_w, 4):
                cl = (80, 165, 85) if (i // 4) % 2 == 0 else (60, 140, 65)
                pygame.draw.rect(bar, cl, (i, 0, 4, 3))
            # Patron de rejilla pixelada
            for gx in range(0, self.disp_w, 32):
                for gy in range(6, self.bar_h, 16):
                    bar.set_at((gx, gy), (38, 68, 48))
                    bar.set_at((gx + 1, gy), (38, 68, 48))
            # Dither decorativo en esquinas
            for dy in range(4, self.bar_h - 4, 2):
                for dx in [8, 12, self.disp_w - 12, self.disp_w - 8]:
                    if (dx + dy) % 4 == 0:
                        bar.set_at((dx, dy), (45, 85, 55))
            self.screen.blit(bar, (0, bar_y))

            bw, bh = 120, 36
            gap = 12
            total_w = bw * 4 + gap * 3
            start_x = (self.disp_w - total_w) // 2
            by = bar_y + (self.bar_h - bh) // 2
            for i, btn in enumerate(self.buttons):
                btn.draw(self.screen, bf, start_x + (bw + gap) * i, by, bw, bh)

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()
