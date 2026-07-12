# Linked List (Lista Enlazada)

## Principales Características
- Colección de nodos donde cada nodo contiene un valor y una referencia al siguiente
- No requiere memoria contigua: los nodos se enlazan mediante punteros
- Inserción y eliminación al inicio en O(1); al final O(n) en lista simple
- Búsqueda O(n): se debe recorrer secuencialmente desde la cabeza
- Tipos: simplemente enlazada, doblemente enlazada y circular

## Elementos que la Componen
- **Nodo (Node)**: estructura con dos campos: dato (valor) y siguiente (referencia)
- **Cabeza (Head)**: puntero al primer nodo de la lista
- **Cola (Tail)**: último nodo, cuyo campo siguiente apunta a nulo (None)
- **Referencia/Siguiente**: enlace que conecta un nodo con el siguiente

## Casos de Uso
- Implementación de pilas, colas y listas de reproducción
- Gestión de memoria dinámica (asignación de bloques libres)
- Historial de navegación (adelante/atrás en navegadores)
- Representación de polinomios y matrices dispersas
- Colisiones en tablas hash (encadenamiento)

## Pseudocódigo

### Recorrido de la Lista
```
funcion recorrer(head):
    actual = head
    mientras actual != nulo:
        imprimir(actual.dato)
        actual = actual.siguiente
```

### Inserción al Inicio
```
funcion insertar_inicio(head, valor):
    nuevo = crear_nodo(valor)
    nuevo.siguiente = head
    retornar nuevo
```

### Eliminación de un Nodo
```
funcion eliminar(head, valor):
    si head == nulo: retornar nulo
    si head.dato == valor: retornar head.siguiente
    actual = head
    mientras actual.siguiente != nulo:
        si actual.siguiente.dato == valor:
            actual.siguiente = actual.siguiente.siguiente
            retornar head
        actual = actual.siguiente
    retornar head
```
