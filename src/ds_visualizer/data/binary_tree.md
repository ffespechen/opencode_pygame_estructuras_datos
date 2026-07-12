# Binary Tree (Árbol Binario)

## Principales Características
- Estructura jerárquica donde cada nodo tiene máximo dos hijos: izquierdo y derecho
- El primer nodo se llama raíz (root); nodos sin hijos son hojas (leaves)
- Altura: número máximo de aristas desde la raíz hasta una hoja
- Árbol binario de búsqueda (BST): hijo izquierdo < padre < hijo derecho
- Recorridos principales: preorden, inorden, postorden y por niveles (BFS)

## Elementos que la Componen
- **Raíz (Root)**: nodo inicial desde donde se accede a toda la estructura
- **Nodo**: contiene un valor, referencia al hijo izquierdo y al hijo derecho
- **Arista (Edge)**: conexión entre un nodo padre y su hijo
- **Hoja (Leaf)**: nodo sin hijos (ambas referencias son nulas)
- **Subárbol**: cualquier nodo junto con todos sus descendientes

## Casos de Uso
- Árboles binarios de búsqueda (BST) para búsquedas, inserciones y eliminaciones eficientes
- Representación de expresiones aritméticas (árboles de expresión)
- Codificación de Huffman para compresión de datos
- Sistemas de archivos jerárquicos (directorios y subdirectorios)
- Montículos (heaps): colas de prioridad, algoritmo de ordenamiento heapsort

## Pseudocódigo

### Recorrido Preorden (raíz → izquierda → derecha)
```
funcion preorden(nodo):
    si nodo == nulo:
        retornar
    procesar(nodo.valor)
    preorden(nodo.izquierdo)
    preorden(nodo.derecho)
```

### Recorrido Inorden (izquierda → raíz → derecha)
```
funcion inorden(nodo):
    si nodo == nulo:
        retornar
    inorden(nodo.izquierdo)
    procesar(nodo.valor)
    inorden(nodo.derecho)
```

### Recorrido Postorden (izquierda → derecha → raíz)
```
funcion postorden(nodo):
    si nodo == nulo:
        retornar
    postorden(nodo.izquierdo)
    postorden(nodo.derecho)
    procesar(nodo.valor)
```
