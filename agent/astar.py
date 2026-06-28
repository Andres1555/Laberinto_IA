"""
Algoritmo A* (A-Star) — Búsqueda Informada.

Implementa el agente explorador que utiliza A* con heurística
de distancia de Manhattan para encontrar la ruta óptima en
un laberinto representado como una grilla 2D.

Función de evaluación:
    f(n) = g(n) + h(n)

Donde:
    g(n) = costo real acumulado desde el inicio hasta n
    h(n) = heurística estimada desde n hasta la meta
    f(n) = costo total estimado del camino a través de n
"""

import heapq
from typing import List, Tuple, Dict, Optional, Set

from agent.node import Node


class AStarAgent:
    """
    Agente explorador basado en el algoritmo A* (A-Star).

    Diseñado para ejecutarse paso a paso, permitiendo la
    visualización en tiempo real de la exploración.

    Atributos principales:
        open_set   : nodos en la frontera (pendientes de evaluar).
        closed_set : nodos ya evaluados.
        optimal_path : ruta óptima encontrada (vacía hasta terminar).
    """

    # Movimientos posibles: arriba, abajo, izquierda, derecha
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, grid: List[List], start: Tuple[int, int], goal: Tuple[int, int]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start = start
        self.goal = goal

        # ── Estructuras del algoritmo A* ──
        self.open_list: list = []                        # Min-heap (cola de prioridad)
        self.open_set: Set[Tuple[int, int]] = set()      # Búsqueda rápida O(1)
        self.closed_set: Set[Tuple[int, int]] = set()    # Nodos ya evaluados
        self.came_from: Dict[Tuple[int, int], Node] = {} # Mapa para reconstruir camino

        # ── Estado de la exploración ──
        self.current_node: Optional[Node] = None
        self.neighbors_being_checked: List[Tuple[int, int]] = []
        self.optimal_path: List[Tuple[int, int]] = []
        self.finished = False
        self.path_found = False

        # ── Estadísticas ──
        self.steps = 0
        self.nodes_explored = 0
        self.current_f: float = 0
        self.current_g: float = 0
        self.current_h: float = 0

        # ── Inicializar con el nodo de inicio ──
        start_node = Node(start)
        start_node.g = 0
        start_node.h = self._heuristic(start)
        start_node.f = start_node.g + start_node.h
        heapq.heappush(self.open_list, start_node)
        self.open_set.add(start)
        self.came_from[start] = start_node

    # ─────────────────────────────────────────────────────────────────────
    # Heurística
    # ─────────────────────────────────────────────────────────────────────
    def _heuristic(self, pos: Tuple[int, int]) -> float:
        """
        Distancia de Manhattan.

            h(n) = |x₁ - x₂| + |y₁ - y₂|

        Es admisible (nunca sobreestima) y consistente para
        movimientos en 4 direcciones, lo que garantiza que
        A* encuentra la ruta óptima.
        """
        return abs(pos[0] - self.goal[0]) + abs(pos[1] - self.goal[1])

    # ─────────────────────────────────────────────────────────────────────
    # Validación
    # ─────────────────────────────────────────────────────────────────────
    def _is_valid(self, pos: Tuple[int, int]) -> bool:
        """Verifica si una posición es transitable (dentro del grid y no es pared)."""
        row, col = pos
        return (0 <= row < self.rows and
                0 <= col < self.cols and
                self.grid[row][col] != 1)

    # ─────────────────────────────────────────────────────────────────────
    # Reconstrucción de ruta
    # ─────────────────────────────────────────────────────────────────────
    def _reconstruct_path(self, node: Node) -> List[Tuple[int, int]]:
        """Reconstruye la ruta óptima siguiendo los punteros 'parent'."""
        path = []
        current = node
        while current is not None:
            path.append(current.position)
            current = current.parent
        path.reverse()
        return path

    # ─────────────────────────────────────────────────────────────────────
    # Paso del algoritmo
    # ─────────────────────────────────────────────────────────────────────
    def step(self) -> bool:
        """
        Ejecuta UN paso del algoritmo A*.

        Retorna:
            True  → el algoritmo terminó (encontró camino o no hay solución).
            False → aún hay nodos por evaluar.

        Procedimiento:
            1. Si la lista abierta está vacía → no hay solución.
            2. Extraer el nodo con menor f(n) de la lista abierta.
            3. Si es la meta → reconstruir y guardar la ruta.
            4. Moverlo a la lista cerrada.
            5. Para cada vecino válido:
               a. Si ya está en la lista cerrada → ignorar.
               b. Calcular g_tentativo = g_actual + 1.
               c. Si es mejor que el camino previo → actualizar.
               d. Si no estaba en la lista abierta → agregarlo.
        """
        if self.finished:
            return True

        # 1. Lista abierta vacía → sin solución
        if not self.open_list:
            self.finished = True
            self.path_found = False
            return True

        # 2. Nodo con menor f(n)
        self.current_node = heapq.heappop(self.open_list)
        current_pos = self.current_node.position
        self.open_set.discard(current_pos)

        # Actualizar estadísticas
        self.steps += 1
        self.nodes_explored += 1
        self.current_f = self.current_node.f
        self.current_g = self.current_node.g
        self.current_h = self.current_node.h

        # 3. ¿Llegamos a la meta?
        if current_pos == self.goal:
            self.optimal_path = self._reconstruct_path(self.current_node)
            self.finished = True
            self.path_found = True
            return True

        # 4. Agregar a lista cerrada
        self.closed_set.add(current_pos)

        # 5. Evaluar vecinos
        self.neighbors_being_checked = []

        for direction in self.DIRECTIONS:
            neighbor_pos = (current_pos[0] + direction[0],
                            current_pos[1] + direction[1])

            if not self._is_valid(neighbor_pos):
                continue

            if neighbor_pos in self.closed_set:
                continue

            self.neighbors_being_checked.append(neighbor_pos)

            # Costo tentativo (cada movimiento cuesta 1)
            tentative_g = self.current_node.g + 1

            # ¿Ya existe un camino mejor?
            if neighbor_pos in self.came_from:
                existing_node = self.came_from[neighbor_pos]
                if tentative_g >= existing_node.g:
                    continue

            # Crear / actualizar nodo vecino
            neighbor_node = Node(neighbor_pos, self.current_node)
            neighbor_node.g = tentative_g
            neighbor_node.h = self._heuristic(neighbor_pos)
            neighbor_node.f = neighbor_node.g + neighbor_node.h

            self.came_from[neighbor_pos] = neighbor_node

            if neighbor_pos not in self.open_set:
                heapq.heappush(self.open_list, neighbor_node)
                self.open_set.add(neighbor_pos)
            else:
                # Re-insertar con mejor costo
                heapq.heappush(self.open_list, neighbor_node)

        return False
