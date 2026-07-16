# Trie (Árbol de Prefijos)

## Principales Características
- Árbol donde cada arista representa un carácter y cada camino desde la raíz una cadena
- Compartir prefijos comunes ahorra espacio y acelera búsquedas por prefijo
- Inserción, búsqueda y borrado de una palabra de longitud k en O(k)
- Ideal para autocompletado y diccionarios de palabras
- Los nodos terminales se marcan para indicar fin de palabra (`*`)

## Elementos que la Componen
- **Raíz (Root)**: nodo vacío de partida
- **Nodo**: mapa de caracteres hijos + bandera de fin de palabra
- **Arista**: transición etiquetada con un carácter
- **Fin de palabra**: marca que el camino actual forma una palabra válida

## Casos de Uso
- Autocompletado en buscadores y editores
- Correctores ortográficos y diccionarios
- Enrutamiento IP (tries de bits / Patricia)
- Filtros de prefijos (URLs, rutas, namespaces)
- Análisis de frecuencias de prefijos en textos

## Pseudocódigo

### Insertar
```
funcion insertar(raiz, palabra):
    actual = raiz
    para cada caracter c en palabra:
        si c no en actual.hijos:
            actual.hijos[c] = crear_nodo()
        actual = actual.hijos[c]
    actual.es_fin = verdadero
```

### Buscar prefijo
```
funcion buscar_prefijo(raiz, prefijo):
    actual = raiz
    para cada caracter c en prefijo:
        si c no en actual.hijos: retornar falso
        actual = actual.hijos[c]
    retornar verdadero
```

### Eliminar (simplificado)
```
funcion eliminar(raiz, palabra):
    // baja por la palabra, quita es_fin
    // elimina nodos hoja sin hijos ni marca de fin (hacia arriba)
```
