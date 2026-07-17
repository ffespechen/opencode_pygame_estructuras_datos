# Hash Set (Conjunto)

## Principales Características
- Colección de **elementos únicos** sin orden garantizado
- Operaciones típicas: add, remove, contains en tiempo promedio O(1)
- Suele implementarse sobre una tabla hash (solo claves, sin valores)
- Soporta operaciones de conjuntos: unión, intersección, diferencia
- No admite duplicados: insertar un elemento existente no cambia el set

## Elementos que la Componen
- **Buckets**: ranuras de la tabla hash
- **Elemento**: valor almacenado (sin par clave-valor)
- **Función hash**: mapea el elemento a un índice de bucket
- **Encadenamiento / open addressing**: resuelve colisiones

## Casos de Uso
- Eliminar duplicados de una colección
- Comprobar pertenencia rápida (listas negras, visitados en BFS/DFS)
- Intersección/unión de etiquetas o permisos
- Conjuntos de vecinos en grafos
- Cachés de claves vistas

## Pseudocódigo

### Add / Contains / Remove
```
funcion add(set, x):
    i = hash(x) mod N
    si x no en set.buckets[i]:
        set.buckets[i].agregar(x)

funcion contains(set, x):
    i = hash(x) mod N
    retornar x en set.buckets[i]

funcion remove(set, x):
    i = hash(x) mod N
    si x en set.buckets[i]:
        set.buckets[i].quitar(x)
```

### Intersección
```
funcion interseccion(A, B):
    R = conjunto_vacio()
    para cada x en A:
        si contains(B, x):
            add(R, x)
    retornar R
```
