"""
Paleta de colores — tema oscuro neón.
"""


class Colors:
    # ── Fondo ──
    BG_DARK       = (6, 18, 10)

    # ── Laberinto ──
    WALL          = (120, 125, 140)
    WALL_HIGHLIGHT = (165, 170, 185)
    WALL_SHADOW   = (80, 85, 100)
    PATH_FREE     = (60, 130, 70)
    FLOOR_LINE    = (50, 115, 60)

    # ── Nodos especiales ──
    START         = (0, 230, 150)
    GOAL          = (255, 80, 90)

    # ── Semáforo A* ──
    OPEN_SET       = (200, 40, 40)      # Rojo — buscando ahora
    OPEN_SET_LIGHT = (230, 70, 70)
    CLOSED_SET       = (255, 210, 40)    # Amarillo — ya explorado
    CLOSED_SET_LIGHT = (255, 230, 90)
    CURRENT        = (255, 255, 100)     # Blanco/amarillo brillante
    OPTIMAL_PATH  = (0, 240, 150)        # Verde — ruta encontrada
    NEIGHBOR_CHECK = (255, 150, 30)      # Naranja
