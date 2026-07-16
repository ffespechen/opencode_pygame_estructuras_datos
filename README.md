# Visualizador de Estructuras de Datos

## Descripción del proyecto

Aplicación interactiva desarrollada con **Pygame** que permite explorar visualmente estructuras de datos fundamentales. El usuario selecciona una estructura desde un menú y accede a una pantalla dividida verticalmente: en la parte superior se muestra una representación gráfica animada de la estructura en acción, y debajo información teórica detallada (características, elementos, casos de uso y pseudocódigo) cargada desde archivos markdown editables.

## Tecnologías / frameworks / librerías utilizadas

- **Python 3.12+**
- **pygame-ce 2.5.7** — fork comunitario activamente mantenido de Pygame (se importa como `pygame`)
- Sin dependencias externas adicionales (el parser de markdown y el renderizado de texto son propios)

## Comandos o instrucciones de instalación

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
cd src
python -m ds_visualizer.main
```

## Descripción detallada de las funcionalidades implementadas

### Menú principal

- Lista de opciones navegable con flechas ↑↓ (y rueda del ratón) y selección con Enter
- Menú con scroll automático cuando hay muchas estructuras
- Estructuras de datos más la opción "Salir" al final, separada por una línea divisoria
- La opción "Salir" aparece en color atenuado cuando no está seleccionada
- Título y subtítulo centrados dinámicamente
- Opción seleccionada resaltada con borde azul y fondo diferenciado

### Pantalla de visualización (dividida verticalmente)

- **Panel superior (45%)**: animación visual de la estructura de datos a ancho completo
  - **Modo demo** (por defecto): cada estructura cicla acciones animadas (~5 s cada una)
  - **Modo interactivo** (`I`): el usuario dispara operaciones con teclas numéricas; el estado persiste hasta `R` (reset)
  - Las operaciones que necesitan datos **piden entrada** (valor, clave, par de vértices, etc.): escribí y confirmá con `Enter` (cancelar con `Esc`)
- **Panel inferior (55%)**: información teórica de la estructura cargada desde archivos `.md` individuales
  - Renderiza títulos, encabezados, listas con viñetas, bloques de código con fondo y texto normal con ajuste de línea
  - Desplazamiento vertical con flechas ↑↓ o rueda del ratón
- **Barra inferior**: atajos a la izquierda; a la derecha, la acción demo o las operaciones disponibles en modo interactivo

### Estructuras de datos implementadas

| Estructura | Demo (automático) | Operaciones interactivas (`1`…`N`) |
|---|---|---|
| **Array / Lista** | Recorrido, búsqueda, inserción, eliminación | Traverse, Search, Insert, Delete |
| **Linked List** | Recorrido, insert head/tail, delete | Traverse, Insert head, Insert tail, Delete head |
| **Doubly Linked List** | Adelante, atrás, insert medio, delete | Forward, Backward, Insert mid, Delete |
| **Stack / Pila** | Push, Peek, Pop | Push, Peek, Pop |
| **Stack (lista enlazada)** | Push/Peek/Pop en HEAD | Push, Peek, Pop |
| **Queue / Cola** | Enqueue, Peek, Dequeue | Enqueue, Peek, Dequeue |
| **Queue (lista enlazada)** | Enqueue TAIL / Dequeue HEAD | Enqueue, Peek, Dequeue |
| **Deque** | Push/Pop en ambos extremos | Push front, Push rear, Pop front, Pop rear |
| **Priority Queue** | Enqueue por prio, Peek, Dequeue | Enqueue, Peek, Dequeue |
| **Hash Map** | Put con colisión, Get, Delete | Put, Get, Remove |
| **Hash Set** | Add, Contains, Remove, Intersección | Add, Contains, Remove |
| **Binary Tree** | Preorden, inorden, postorden, insert BST | Preorden, Inorden, Postorden, Insert |
| **AVL Tree** | Desbalance LL/RR y rotaciones | Insert, Delete |
| **Heap** | Insert bubble-up, extract, Peek, Heapify | Insert, Extract-min, Peek |
| **Trie** | Insert CAT/CAR, prefijo, delete | Insert, Search, Delete |
| **Grafo** | BFS, DFS, vértice, arista | BFS, DFS, Add vertex, Add edge |
| **Union-Find** | Find, Union, path compression | Find, Union |
| **Sparse Matrix** | Vista COO, insert, search, traverse | Insert, Search, Traverse |

### Redimensionamiento de ventana

- Ventana redimensionable (`pygame.RESIZABLE`) con tamaño mínimo de 800×600
- Layout dinámico: panel superior 45% / panel inferior 55% del alto de contenido
- El contenido del panel de información se re-renderiza al nuevo ancho completo
- Las animaciones usan la geometría del rectángulo asignado (escalan con la ventana)

### Atajos de teclado

| Combinación | Acción |
|---|---|
| `Ctrl+Q` | Salir de la aplicación (desde cualquier pantalla) |
| `↑ ↓` | Navegar opciones del menú / desplazar panel de información |
| `Enter` | Seleccionar estructura en el menú |
| `ESC` | Volver al menú desde la visualización |
| `I` | Alternar modo demo ↔ interactivo (en visualización) |
| `R` | Reiniciar la estructura al estado inicial (modo interactivo) |
| `1`…`9` | Ejecutar la operación correspondiente (también activa el modo interactivo) |
| Texto + `Enter` | Completar el dato pedido por la operación (ej. par `B F` para una arista) |
| `Esc` | Cancelar el prompt de entrada; si no hay prompt, volver al menú |
| `Rueda ratón` | Desplazar panel de información |

### Archivos de datos

Cada estructura de datos tiene su propio archivo `.md` en `src/ds_visualizer/data/` con la siguiente estructura:
1. Título (`#`)
2. Principales Características (`##`)
3. Elementos que la Componen (`##`)
4. Casos de Uso (`##`)
5. Pseudocódigo (`##` con bloques de código)
