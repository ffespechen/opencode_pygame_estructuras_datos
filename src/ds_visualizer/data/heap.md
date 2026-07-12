# Heap / Montículo

## Principales Características
- Árbol binario completo donde cada nodo cumple la propiedad de heap: padre ≤ hijos (min-heap) o padre ≥ hijos (max-heap)
- La raíz siempre contiene el elemento mínimo (min-heap) o máximo (max-heap)
- Inserción O(log n): se inserta al final y se aplica bubble-up (flotar) para restaurar la propiedad
- Extracción del mínimo/máximo O(log n): se intercambia raíz con último, se elimina y se aplica bubble-down (hundir)
- Se implementa típicamente con un array: hijo izquierdo en 2i+1, hijo derecho en 2i+2, padre en (i-1)//2

## Elementos que la Componen
- **Raíz**: primer elemento del array (índice 0), contiene el valor mínimo (min-heap) o máximo (max-heap)
- **Nodo**: cada posición del array; cumple la propiedad de heap respecto a sus hijos
- **Padre**: nodo en índice `i` cuyo padre está en `(i-1)//2`
- **Hijo izquierdo**: nodo en índice `2i+1`
- **Hijo derecho**: nodo en índice `2i+2`

## Casos de Uso
- Colas de prioridad (sistemas operativos, planificación de tareas)
- Algoritmo de Dijkstra y Prim (caminos mínimos en grafos)
- HeapSort: algoritmo de ordenamiento O(n log n) in-place
- Selección de los k elementos más grandes/pequeños (Top-K)
- Simulación de eventos discretos (próximo evento = mínimo timestamp)

## Pseudocódigo

### Inserción con Bubble-Up
```
funcion insertar(heap, valor):
    heap.agregar(valor)
    i = longitud(heap) - 1
    mientras i > 0:
        padre = (i - 1) // 2
        si heap[i] >= heap[padre]:
            romper
        intercambiar(heap[i], heap[padre])
        i = padre
```

### Extracción del Mínimo con Bubble-Down
```
funcion extraer_min(heap):
    si heap vacio: error
    minimo = heap[0]
    heap[0] = heap[longitud - 1]
    heap.eliminar_ultimo()
    i = 0
    mientras verdadero:
        izq = 2 * i + 1
        der = 2 * i + 2
        menor = i
        si izq < longitud y heap[izq] < heap[menor]:
            menor = izq
        si der < longitud y heap[der] < heap[menor]:
            menor = der
        si menor == i:
            romper
        intercambiar(heap[i], heap[menor])
        i = menor
    retornar minimo
```

### Peek (Consultar Mínimo)
```
funcion peek(heap):
    si heap vacio: error
    retornar heap[0]
```
