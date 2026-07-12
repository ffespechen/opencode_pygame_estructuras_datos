# Hash Map / Diccionario

## Principales Características
- Estructura que asocia claves (keys) con valores (values) mediante una función hash
- Búsqueda, inserción y eliminación en O(1) promedio, O(n) en el peor caso
- La función hash transforma la clave en un índice de un array subyacente (bucket)
- Colisiones: cuando dos claves generan el mismo índice; se resuelven con encadenamiento o direccionamiento abierto
- Factor de carga: relación entre elementos almacenados y capacidad total; afecta el rendimiento

## Elementos que la Componen
- **Clave (Key)**: identificador único que se pasa a la función hash para obtener el bucket
- **Valor (Value)**: dato asociado a la clave
- **Función hash**: transforma la clave en un entero (índice) — debe ser determinista y uniforme
- **Buckets**: posiciones del array subyacente; cada uno puede contener uno o más pares clave-valor
- **Lista de colisión**: estructura (lista enlazada o array) dentro de un bucket para manejar claves que colisionan

## Casos de Uso
- Implementación nativa de diccionarios en Python, JavaScript (objetos/Map), Java (HashMap)
- Cachés y memoización (almacenar resultados de funciones costosas)
- Indexación en bases de datos (hash indexes)
- Conteo de frecuencias (contar palabras, caracteres, eventos)
- Detección de duplicados en conjuntos de datos grandes

## Pseudocódigo

### Inserción (Put)
```
funcion put(tabla, clave, valor):
    indice = hash(clave) mod tabla.capacidad
    bucket = tabla.buckets[indice]
    para cada par en bucket:
        si par.clave == clave:
            par.valor = valor
            retornar
    bucket.agregar(nuevo_par(clave, valor))
    tabla.tamano += 1
```

### Búsqueda (Get)
```
funcion get(tabla, clave):
    indice = hash(clave) mod tabla.capacidad
    bucket = tabla.buckets[indice]
    para cada par en bucket:
        si par.clave == clave:
            retornar par.valor
    error "Clave no encontrada"
```

### Eliminación (Delete)
```
funcion delete(tabla, clave):
    indice = hash(clave) mod tabla.capacidad
    bucket = tabla.buckets[indice]
    para i desde 0 hasta longitud(bucket) - 1:
        si bucket[i].clave == clave:
            bucket.eliminar(i)
            tabla.tamano -= 1
            retornar
    error "Clave no encontrada"
```
