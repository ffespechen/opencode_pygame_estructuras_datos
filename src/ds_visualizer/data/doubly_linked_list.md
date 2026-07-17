# Doubly Linked List (Lista Doblemente Enlazada)

## Principales Características
- Cada nodo tiene referencias al siguiente **y** al anterior
- Recorrido bidireccional: de HEAD a TAIL y de TAIL a HEAD
- Inserción y eliminación en cualquier posición en O(1) si se tiene el puntero al nodo
- Búsqueda sigue siendo O(n), pero se puede empezar desde cualquiera de los extremos
- Usa más memoria que la lista simple (dos punteros por nodo)

## Elementos que la Componen
- **Nodo (Node)**: dato, `siguiente` (next) y `anterior` (prev)
- **Cabeza (Head)**: puntero al primer nodo; su `anterior` es nulo
- **Cola (Tail)**: puntero al último nodo; su `siguiente` es nulo
- **Enlaces bidireccionales**: permiten navegar en ambos sentidos

## Casos de Uso
- Historial de navegación (adelante / atrás) en navegadores
- Listas de reproducción con desplazamiento en ambos sentidos
- Implementación de deques (colas de doble extremo)
- Editores de texto (cursor hacia adelante y atrás)
- Cachés LRU (mover nodos al frente/final eficientemente)

## Pseudocódigo

### Recorrido hacia adelante
```
funcion recorrer_adelante(head):
    actual = head
    mientras actual != nulo:
        imprimir(actual.dato)
        actual = actual.siguiente
```

### Recorrido hacia atrás
```
funcion recorrer_atras(tail):
    actual = tail
    mientras actual != nulo:
        imprimir(actual.dato)
        actual = actual.anterior
```

### Inserción en medio (después de un nodo)
```
funcion insertar_despues(nodo, valor):
    nuevo = crear_nodo(valor)
    nuevo.siguiente = nodo.siguiente
    nuevo.anterior = nodo
    si nodo.siguiente != nulo:
        nodo.siguiente.anterior = nuevo
    nodo.siguiente = nuevo
```

### Eliminación de un nodo
```
funcion eliminar(nodo, head, tail):
    si nodo.anterior != nulo:
        nodo.anterior.siguiente = nodo.siguiente
    sino:
        head = nodo.siguiente
    si nodo.siguiente != nulo:
        nodo.siguiente.anterior = nodo.anterior
    sino:
        tail = nodo.anterior
    retornar head, tail
```
