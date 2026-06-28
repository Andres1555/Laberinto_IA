"""
Constantes globales del proyecto.

Define tamaños de celda, dimensiones del panel lateral,
FPS y estados de la aplicación.
"""

from enum import Enum


# ─────────────────────────────────────────────────────────────────────────────
# DIMENSIONES
# ─────────────────────────────────────────────────────────────────────────────
CELL_SIZE = 44          # Tamaño de cada celda
PANEL_WIDTH = 0         # Sin panel lateral
FPS = 120               # Cuadros por segundo (más fluido)


# ─────────────────────────────────────────────────────────────────────────────
# ESTADOS DE LA APLICACIÓN
# ─────────────────────────────────────────────────────────────────────────────
class AppState(Enum):
    """Estados posibles del sistema de exploración."""
    IDLE = "idle"                # Esperando que el usuario inicie
    EXPLORING = "exploring"      # A* en ejecución
    PAUSED = "paused"            # Exploración pausada
    PATH_FOUND = "path_found"    # Ruta óptima encontrada
    NO_PATH = "no_path"          # No existe ruta posible
