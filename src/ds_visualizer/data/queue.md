# Queue / Cola

## Principales Características
- Estructura FIFO (First In, First Out): el primero en entrar es el primero en salir
- Dos extremos: frente (front) para extraer y final (rear) para insertar
- Operaciones básicas: enqueue (encolar) y dequeue (desencolar), ambas O(1)
- Variantes: cola circular, cola de prioridad, cola doble (deque)
- Puede implementarse con arrays circulares o listas enlazadas

## Elementos que la Componen
- **Frente (Front)**: puntero al primer elemento (próximo a salir)
- **Final (Rear)**: puntero al último elemento insertado
- **Elementos**: valores en orden de llegada
- **Capacidad**: límite de la cola (en implementaciones con array fijo)

## Casos de Uso
- Planificación de procesos en sistemas operativos (round-robin)
- Gestión de trabajos de impresión (spooler de impresora)
- Buffers de entrada/salida y manejo de eventos asíncronos
- Algoritmo BFS (Breadth-First Search) en grafos
- Simulación de líneas de espera (colas de banco, supermercado)

## Pseudocódigo

### Enqueue (Encolar)
```
funcion enqueue(cola, valor):
    si cola.llena():
        error "Cola llena"
    cola.final = (cola.final + 1) mod capacidad
    cola.datos[cola.final] = valor
    cola.tamano += 1
```

### Dequeue (Desencolar)
```
funcion dequeue(cola):
    si cola.vacia():
        error "Cola vacía"
    valor = cola.datos[cola.frente]
    cola.frente = (cola.frente + 1) mod capacidad
    cola.tamano -= 1
    retornar valor
```

### Peek (Consultar Frente)
```
funcion peek(cola):
    si cola.vacia():
        error "Cola vacía"
    retornar cola.datos[cola.frente]
```
