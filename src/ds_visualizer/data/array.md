# Array / Lista

## Principales Características
- Colección ordenada de elementos del mismo tipo
- Acceso aleatorio en tiempo constante O(1) mediante índice numérico
- Los elementos ocupan posiciones contiguas en memoria (arrays estáticos)
- Tamaño fijo en arrays clásicos, dinámico en listas redimensionables
- Inserción y eliminación en posiciones intermedias requiere desplazamiento O(n)

## Elementos que la Componen
- **Índices**: enteros consecutivos (0, 1, 2, ...) que identifican cada posición
- **Elementos/Valores**: datos almacenados en cada celda del arreglo
- **Longitud (n)**: cantidad actual de elementos en la estructura
- **Capacidad**: espacio total reservado (en implementaciones con tamaño fijo)

## Casos de Uso
- Almacenamiento de colecciones secuenciales (notas de alumnos, productos)
- Implementación base de otras estructuras: pilas, colas, tablas hash
- Buffers de memoria y colas de mensajes en sistemas operativos
- Vectores y matrices en computación científica y gráficos
- Cachés y tablas de búsqueda por índice

## Pseudocódigo

### Búsqueda Lineal
```
funcion busqueda_lineal(arr, valor):
    para i desde 0 hasta longitud(arr) - 1:
        si arr[i] == valor:
            retornar i
    retornar -1
```

### Inserción en Posición
```
funcion insertar(arr, indice, valor):
    si indice < 0 o indice >= capacidad:
        error "Índice fuera de rango"
    para i desde longitud - 1 hasta indice (decreciente):
        arr[i + 1] = arr[i]
    arr[indice] = valor
    longitud += 1
```

### Eliminación por Índice
```
funcion eliminar(arr, indice):
    si indice < 0 o indice >= longitud:
        error "Índice inválido"
    para i desde indice hasta longitud - 2:
        arr[i] = arr[i + 1]
    longitud -= 1
```
