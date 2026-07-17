# Queue con Lista Enlazada (Cola)

## Principales Características
- Misma semántica FIFO que una cola clásica, respaldada por nodos enlazados
- Se mantienen dos punteros: **FRONT = HEAD** y **REAR = TAIL**
- Enqueue inserta al final (TAIL) y Dequeue elimina al inicio (HEAD), ambos O(1)
- Sin redimensionamiento: crece solo con la memoria disponible
- Peek consulta el dato de HEAD sin modificar la cola

## Elementos que la Componen
- **Nodo**: valor + referencia al siguiente
- **FRONT / HEAD**: primer nodo; es el próximo a desencolar
- **REAR / TAIL**: último nodo; es donde se encolan nuevos elementos
- **Vacía**: cuando HEAD y TAIL son nulos

## Casos de Uso
- Colas de impresión o de mensajes con tamaño impredecible
- BFS en grafos cuando el número de nodos no está acotado
- Buffers de entrada/salida asíncronos
- Planificación de procesos (ready queue)
- Cuando se quiere evitar el costo de un buffer circular redimensionable

## Pseudocódigo

### Enqueue (insertar en TAIL)
```
funcion enqueue(queue, valor):
    nuevo = crear_nodo(valor)
    si queue.tail == nulo:
        queue.head = nuevo
        queue.tail = nuevo
    sino:
        queue.tail.siguiente = nuevo
        queue.tail = nuevo
```

### Peek
```
funcion peek(queue):
    si queue.head == nulo: error "cola vacia"
    retornar queue.head.dato
```

### Dequeue (eliminar HEAD)
```
funcion dequeue(queue):
    si queue.head == nulo: error "cola vacia"
    valor = queue.head.dato
    queue.head = queue.head.siguiente
    si queue.head == nulo:
        queue.tail = nulo
    retornar valor
```
