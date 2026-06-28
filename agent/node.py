"""
Nodo para el algoritmo A*.

Cada nodo almacena su posición en el laberinto, una referencia
al nodo padre (para reconstruir la ruta) y los costos g, h, f.
"""

from typing import Tuple, Optional


class Node:
    """
    Representa un nodo en el grafo de búsqueda A*.

    Atributos:
        position : (fila, columna) en el laberinto.
        parent   : nodo padre para reconstruir el camino.
        g        : costo real desde el inicio hasta este nodo.
        h        : heurística estimada hasta la meta.
        f        : costo total estimado (f = g + h).
    """

    def __init__(self, position: Tuple[int, int], parent: Optional["Node"] = None):
        self.position = position
        self.parent = parent
        self.g: float = 0
        self.h: float = 0
        self.f: float = 0



    def __lt__(self, other: "Node") -> bool:
        return self.f < other.f

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return self.position == other.position

    def __hash__(self) -> int:
        return hash(self.position)

    def __repr__(self) -> str:
        return f"Node(pos={self.position}, f={self.f:.1f}, g={self.g:.1f}, h={self.h:.1f})"
