# Stack / Pila

## Principales Características
- Estructura LIFO (Last In, First Out): el último en entrar es el primero en salir
- Solo se accede al elemento en el tope (cima) de la pila
- Operaciones fundamentales: push (apilar), pop (desapilar), peek (consultar tope)
- Todas las operaciones básicas son O(1)
- Puede implementarse con arrays o listas enlazadas

## Elementos que la Componen
- **Tope/Cima (Top)**: referencia al último elemento insertado
- **Elementos**: valores almacenados en orden de inserción
- **Capacidad máxima**: límite opcional cuando se implementa con array fijo
- **Base (Bottom)**: primer elemento insertado (no se accede directamente)

## Casos de Uso
- Gestión de llamadas a funciones (call stack en lenguajes de programación)
- Evaluación de expresiones matemáticas (notación polaca inversa)
- Algoritmo de backtracking (vuelta atrás) y recorrido en profundidad (DFS)
- Deshacer/Rehacer (Undo/Redo) en editores de texto y gráficos
- Verificación de paréntesis, llaves y corchetes balanceados

## Pseudocódigo

### Push (Apilar)
```
funcion push(pila, valor):
    si pila.llena():
        error "Desbordamiento de pila (stack overflow)"
    pila.tope += 1
    pila.datos[pila.tope] = valor
```

### Pop (Desapilar)
```
funcion pop(pila):
    si pila.vacia():
        error "Subdesbordamiento de pila (stack underflow)"
    valor = pila.datos[pila.tope]
    pila.tope -= 1
    retornar valor
```

### Peek (Consultar Tope)
```
funcion peek(pila):
    si pila.vacia():
        error "Pila vacía"
    retornar pila.datos[pila.tope]
```
