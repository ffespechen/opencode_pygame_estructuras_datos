# Deque (Cola de Doble Extremo)

## Principales Características
- Permite insertar y eliminar elementos en **ambos extremos** (frente y final)
- Todas las operaciones básicas (push/pop front/rear) son O(1)
- Generaliza la pila y la cola: puede comportarse como cualquiera de las dos
- Suele implementarse con lista doblemente enlazada o con buffer circular
- Estructura lineal ordenada por posición de inserción

## Elementos que la Componen
- **Front (frente)**: extremo izquierdo; pop/push front actúan aquí
- **Rear (final)**: extremo derecho; pop/push rear actúan aquí
- **Nodos o celdas**: contenedores de los valores almacenados
- **Tamaño**: cantidad actual de elementos

## Casos de Uso
- Algoritmos de ventanas deslizantes (máximo/mínimo en rango)
- Palíndromos: comparar extremos y avanzar hacia el centro
- Historial con undo/redo limitado
- Planificación de tareas con prioridad en ambos extremos
- Implementación eficiente de BFS 0-1 (grafos con aristas 0/1)

## Pseudocódigo

### Push front / Push rear
```
funcion push_front(deque, valor):
    nuevo = crear_nodo(valor)
    nuevo.siguiente = deque.front
    si deque.front != nulo:
        deque.front.anterior = nuevo
    deque.front = nuevo
    si deque.rear == nulo:
        deque.rear = nuevo

funcion push_rear(deque, valor):
    nuevo = crear_nodo(valor)
    nuevo.anterior = deque.rear
    si deque.rear != nulo:
        deque.rear.siguiente = nuevo
    deque.rear = nuevo
    si deque.front == nulo:
        deque.front = nuevo
```

### Pop front / Pop rear
```
funcion pop_front(deque):
    si deque.front == nulo: error "vacia"
    valor = deque.front.dato
    deque.front = deque.front.siguiente
    si deque.front != nulo:
        deque.front.anterior = nulo
    sino:
        deque.rear = nulo
    retornar valor

funcion pop_rear(deque):
    si deque.rear == nulo: error "vacia"
    valor = deque.rear.dato
    deque.rear = deque.rear.anterior
    si deque.rear != nulo:
        deque.rear.siguiente = nulo
    sino:
        deque.front = nulo
    retornar valor
```
