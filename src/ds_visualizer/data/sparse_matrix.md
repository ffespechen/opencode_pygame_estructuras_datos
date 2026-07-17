# Sparse Matrix (Matriz Dispersa)

## Principales Características
- Matriz donde la **gran mayoría de elementos son cero**
- Guardar todos los ceros desperdicia memoria; se almacenan solo no-ceros
- Formatos comunes: **COO** (coordenadas), CSR/CSC (filas/columnas comprimidas)
- Acceso a un elemento concreto puede ser O(k) o O(log k) según la representación
- Operaciones algebraicas se optimizan saltando ceros

## Elementos que la Componen
- **Entrada no-cero**: triple (fila, columna, valor) en formato COO
- **Dimensiones**: número de filas y columnas lógicas
- **Índices**: coordenadas de las celdas con valor ≠ 0
- **Estructura auxiliar**: arrays de punteros en CSR/CSC

## Casos de Uso
- Grafos como matrices de adyacencia dispersas
- Sistemas de ecuaciones lineales grandes (FEM, circuitos)
- Recomendadores y matrices usuario-ítem
- Procesamiento de imágenes con pocos píxeles activos
- NLP: matrices término-documento

## Pseudocódigo

### Insertar (COO)
```
funcion insertar(matriz, i, j, valor):
    si valor == 0: retornar
    para cada entrada e en matriz.entradas:
        si e.fila == i y e.col == j:
            e.valor = valor
            retornar
    matriz.entradas.agregar((i, j, valor))
```

### Buscar
```
funcion buscar(matriz, i, j):
    para cada (f, c, v) en matriz.entradas:
        si f == i y c == j: retornar v
    retornar 0
```

### Recorrer no-ceros
```
funcion recorrer(matriz):
    para cada (f, c, v) en matriz.entradas:
        procesar(f, c, v)
```
