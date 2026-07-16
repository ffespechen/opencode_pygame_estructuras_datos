# Priority Queue (Cola de Prioridad)

## Principales Características
- Cada elemento tiene una **prioridad**; el de mayor prioridad sale primero
- No es FIFO puro: el orden de salida depende de la prioridad, no solo del tiempo
- Suele implementarse con un **heap**, pero conceptualmente es una cola ordenada
- Enqueue O(log n) y Dequeue O(log n) con heap; Peek O(1)
- Variantes: min-priority (menor número primero) o max-priority

## Elementos que la Componen
- **Elemento**: valor + prioridad asociada
- **FRONT**: extremo con la máxima prioridad actual
- **Comparador**: define qué prioridad es “mejor”
- **Estructura interna**: heap, árbol balanceado o lista ordenada

## Casos de Uso
- Planificación de procesos / tareas urgentes
- Algoritmo de Dijkstra (nodos por distancia)
- Colas de eventos en simulaciones
- Sistemas de impresión por prioridad
- A* y otros algoritmos de búsqueda informada

## Pseudocódigo

### Enqueue
```
funcion enqueue(pq, valor, prioridad):
    // con heap: insertar y bubble-up
    pq.insertar((prioridad, valor))
```

### Peek / Dequeue
```
funcion peek(pq):
    retornar pq.raiz   // máxima prioridad

funcion dequeue(pq):
    valor = pq.raiz
    pq.extraer_raiz()  // bubble-down
    retornar valor
```
