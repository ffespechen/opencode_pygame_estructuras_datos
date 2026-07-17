# Stack con Lista Enlazada (Pila)

## Principales Características
- Misma semántica LIFO que una pila clásica, pero respaldada por nodos enlazados
- El **TOP** coincide con el **HEAD** de la lista: push y pop solo tocan el inicio
- Push y Pop en O(1); no hay redimensionamiento de array
- Peek consulta el dato de HEAD sin modificar la estructura
- Ideal cuando el tamaño máximo de la pila es desconocido o muy variable

## Elementos que la Componen
- **Nodo**: valor + referencia al siguiente
- **TOP / HEAD**: puntero al nodo del tope (primer nodo de la lista)
- **Enlace siguiente**: conecta cada nodo con el que quedó debajo en la pila
- **Vacía**: cuando HEAD es nulo

## Casos de Uso
- Evaluación de expresiones y parsers (cuando el tamaño crece dinámicamente)
- Backtracking y DFS recursivo simulado con pila dinámica
- Undo/redo en editores
- Llamadas a funciones (modelo conceptual de call stack)
- Cuando se quiere evitar el costo de redimensionar un array subyacente

## Pseudocódigo

### Push (insertar en HEAD)
```
funcion push(stack, valor):
    nuevo = crear_nodo(valor)
    nuevo.siguiente = stack.head
    stack.head = nuevo
```

### Peek
```
funcion peek(stack):
    si stack.head == nulo: error "pila vacia"
    retornar stack.head.dato
```

### Pop (eliminar HEAD)
```
funcion pop(stack):
    si stack.head == nulo: error "pila vacia"
    valor = stack.head.dato
    stack.head = stack.head.siguiente
    retornar valor
```
