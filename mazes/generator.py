"""
Generador de laberintos aleatorios.

Usa el algoritmo de Recursive Backtracker (DFS aleatorizado)
para generar laberintos perfectos.
"""

import random
from typing import List, Tuple, Dict


def generate_maze(rows: int = 21, cols: int = 21) -> Dict:
    """
    Genera un laberinto aleatorio.

    Retorna un dict con formato compatible con MAZES:
        { "name": ..., "grid": [[0,1,'S',...]] }

    Si rows o cols son pares se genera al siguiente impar y se recorta.
    """

    gen_rows = rows if rows % 2 else rows + 1
    gen_cols = cols if cols % 2 else cols + 1

    grid = [[1] * gen_cols for _ in range(gen_rows)]

    start_r = random.randrange(1, gen_rows - 1, 2)
    start_c = random.randrange(1, gen_cols - 1, 2)

    def carve(r: int, c: int):
        grid[r][c] = 0
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 1 <= nr < gen_rows - 1 and 1 <= nc < gen_cols - 1 and grid[nr][nc] == 1:
                grid[r + dr // 2][c + dc // 2] = 0
                carve(nr, nc)

    carve(start_r, start_c)

    # Colocar S
    sc = 1
    candidates_s = [(r, sc) for r in range(1, gen_rows - 1) if grid[r][sc] == 0]
    if candidates_s:
        sr, sc = random.choice(candidates_s)
        grid[sr][sc] = 'S'

    # Colocar G
    gc = gen_cols - 3 if (gen_cols - 2) % 2 == 0 else gen_cols - 2
    candidates_g = [(r, gc) for r in range(1, gen_rows - 1) if grid[r][gc] == 0]
    if candidates_g:
        gr, gc = random.choice(candidates_g)
        grid[gr][gc] = 'G'

    # Recortar al tamaño solicitado
    grid = [row[:cols] for row in grid[:rows]]

    return {
        "name": f"Aleatorio ({rows}x{cols})",
        "grid": grid,
    }
