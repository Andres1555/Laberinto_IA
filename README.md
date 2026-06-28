# Agente Explorador de Laberinto con A* (A-Star)

**Materia:** Inteligencia Artificial  
**Prof.** Manuel Paniccia

---

## Descripcion

Agente autonomo que explora un laberinto en tiempo real utilizando el algoritmo de **Busqueda Informada A\* (A-Star)** para encontrar la ruta optima desde el punto de inicio (S) hasta la meta.

El sistema visualiza en una ventana de 1200x870:
- El **proceso de exploracion** paso a paso (ccmo A* evalua los nodos)
- La **lista abierta** en rojo (frontera por evaluar)
- La **lista cerrada** en amarillo (nodos ya evaluados)
- Los **vecinos** siendo revisados (borde naranja)
- La **ruta optima** en verde con animacion de aparicion
- Panel lateral izquierdo con informacion del HUD y leyenda de colores/letras

## Algoritmo A* (A-Star)

### Funcion de evaluacion

```
f(n) = g(n) + h(n)
```

- **g(n)**: Costo real acumulado desde el inicio hasta el nodo `n`
- **h(n)**: Heuristica estimada desde `n` hasta la meta
- **f(n)**: Costo total estimado del camino pasando por `n`

### Heuristica: Distancia de Manhattan

```
h(n) = |x1 - x2| + |y1 - y2|
```

Admisible y consistente para movimientos en 4 direcciones, garantizando la ruta �ptima.

## Requisitos

- Python 3.13+
- pygame-ce 2.5.7

## Instalacion

```bash
pip install pygame-ce
```

## Ejecucion

```bash
python laberinto_ia.py
```



## Laberintos Disponibles

1. **Clasico** — Laberinto tradicional con caminos serpenteantes (1212)
2. **Espiral** — Estructura en espiral que obliga a recorrer largo camino (1212)
3. **Multiples Caminos** — Varias rutas posibles, A* encuentra la ptima (1212)
4. **Denso** — Laberinto compacto con pocos espacios libres (1212)

Ademas se puede generar un laberinto aleatorio (1111) con el boton "ALEATORIO" o la tecla `G`.

## Leyenda Visual

| Color   | Significado                  |
|---------|------------------------------|
| Rojo    | Lista abierta (buscando)     |
| Amarillo| Lista cerrada (explorado)    |
| Verde   | Ruta optima encontrada       |
| Naranja| Vecinos siendo evaluados     |

| Letra | Significado        |
|-------|--------------------|
| f     | Costo total        |
| g     | Costo desde inicio |
| h     | Heuristica         |

## Estructura del Proyecto

```
Laberinto_IA/
  laberinto_ia.py       # Punto de entrada
  app.py                # Aplicacion principal (MazeExplorer)
  config/
    constants.py        # Constantes y estados
    colors.py           # Paleta de colores oscuro neon
  agent/
    astar.py            # Algoritmo A* paso a paso
    node.py             # Nodo con f=g+h y comparacion para heap
  mazes/
    definitions.py      # 4 laberintos predefinidos (1212)
    generator.py        # Generador aleatorio (Recursive Backtracker)
  ui/
    renderer.py         # Renderizado del grid, semaforo, info de celdas
```
