# Grafo (Graph)

## Principales Características
- Conjunto de vértices (nodos) conectados por aristas (edges, arcos)
- Puede ser dirigido (aristas con dirección) o no dirigido (conexión bidireccional)
- Puede ser ponderado (aristas con peso/valor) o no ponderado
- Representaciones: matriz de adyacencia o lista de adyacencia
- Recorridos fundamentales: BFS (anchura) y DFS (profundidad)

## Elementos que la Componen
- **Vértice/Nodo**: unidad fundamental del grafo que representa una entidad
- **Arista/Arco**: conexión entre dos vértices; puede tener dirección y/o peso
- **Grado**: número de aristas incidentes en un vértice (en dirigidos: grado de entrada y salida)
- **Camino (Path)**: secuencia de vértices conectados por aristas
- **Ciclo**: camino que empieza y termina en el mismo vértice

## Casos de Uso
- Redes sociales: vértices = personas, aristas = amistades/seguidores
- Mapas y navegación GPS: vértices = ubicaciones, aristas = rutas con peso = distancia
- Internet: enrutamiento de paquetes entre routers (algoritmo de Dijkstra)
- Dependencias en sistemas de compilación (Makefiles, orden topológico)
- Recomendaciones en comercio electrónico (grafos de productos y usuarios)

## Pseudocódigo

### BFS — Recorrido en Anchura
```
funcion bfs(grafo, inicio):
    cola = nueva_cola()
    visitado = conjunto_vacio()
    cola.encolar(inicio)
    visitado.agregar(inicio)
    mientras cola no vacia:
        v = cola.desencolar()
        procesar(v)
        para cada vecino w de v:
            si w no esta en visitado:
                visitado.agregar(w)
                cola.encolar(w)
```

### DFS — Recorrido en Profundidad
```
funcion dfs(grafo, inicio):
    pila = nueva_pila()
    visitado = conjunto_vacio()
    pila.push(inicio)
    mientras pila no vacia:
        v = pila.pop()
        si v no esta en visitado:
            visitado.agregar(v)
            procesar(v)
            para cada vecino w de v:
                si w no esta en visitado:
                    pila.push(w)
```
