# AVL Tree (Árbol AVL)

## Principales Características
- Árbol binario de búsqueda **auto-balanceado**
- En cada nodo, la diferencia de alturas de subárboles (factor de balance) es −1, 0 o +1
- Inserción y eliminación pueden requerir **rotaciones** para restaurar el equilibrio
- Altura O(log n) garantizada → búsqueda, inserción y borrado O(log n)
- Inventado por Adelson-Velsky y Landis (1962)

## Elementos que la Componen
- **Nodo**: valor, hijo izquierdo, hijo derecho y altura (o factor de balance)
- **Factor de balance (BF)**: altura(izq) − altura(der)
- **Rotación simple**: LL (derecha) o RR (izquierda)
- **Rotación doble**: LR o RL (combinación de dos simples)

## Casos de Uso
- Diccionarios y mapas ordenados con garantías estrictas de tiempo
- Índices en memoria que requieren orden y búsqueda rápida
- Alternativa a árboles rojo-negro cuando se prioriza un balance más estricto
- Sistemas donde las consultas son frecuentes y las actualizaciones moderadas

## Pseudocódigo

### Factor de balance
```
funcion bf(nodo):
    retornar altura(nodo.izq) - altura(nodo.der)
```

### Rotación derecha (LL)
```
funcion rotar_derecha(y):
    x = y.izq
    T2 = x.der
    x.der = y
    y.izq = T2
    actualizar_alturas(y, x)
    retornar x
```

### Rotación izquierda (RR)
```
funcion rotar_izquierda(x):
    y = x.der
    T2 = y.izq
    y.izq = x
    x.der = T2
    actualizar_alturas(x, y)
    retornar y
```
