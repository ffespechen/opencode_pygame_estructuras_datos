# Union-Find (Conjuntos Disjuntos / DSU)

## Principales Características
- Mantiene una partición de elementos en **conjuntos disjuntos**
- Operaciones principales: **Find** (raíz del conjunto) y **Union** (fusionar dos conjuntos)
- Con *union by rank* y *path compression* las operaciones son casi O(1) amortizado
- Representación típica: array/mapa de padres formando un bosque de árboles
- También llamado Disjoint Set Union (DSU)

## Elementos que la Componen
- **Elemento**: nodo identificado (A, B, C, …)
- **Parent**: puntero al representante/padre en el árbol
- **Raíz**: elemento cuyo parent es él mismo; identifica el conjunto
- **Rank / tamaño**: heurística para unir el árbol más chico bajo el más grande

## Casos de Uso
- Detectar ciclos en grafos (Kruskal)
- Componentes conexas online
- Problemas de conectividad dinámica
- Equivalencias y particiones (redes, amigos, islas)
- Clustering incremental

## Pseudocódigo

### Find con path compression
```
funcion find(x):
    si parent[x] != x:
        parent[x] = find(parent[x])
    retornar parent[x]
```

### Union por raíz
```
funcion union(a, b):
    ra = find(a)
    rb = find(b)
    si ra == rb: retornar
    parent[rb] = ra   // o según rank
```
