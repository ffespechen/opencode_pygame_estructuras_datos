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

- Lista de opciones navegable con flechas ↑↓ y selección con Enter
- Estructuras de datos más la opción "Salir" al final, separada por una línea divisoria
- La opción "Salir" aparece en color atenuado cuando no está seleccionada
- Título y subtítulo centrados dinámicamente
- Opción seleccionada resaltada con borde azul y fondo diferenciado

### Pantalla de visualización (dividida verticalmente)

- **Panel superior (45%)**: animación visual de la estructura de datos a ancho completo
  - Cada estructura tiene 4 acciones que se alternan cíclicamente (5 segundos cada una)
- **Panel inferior (55%)**: información teórica de la estructura cargada desde archivos `.md` individuales
  - Renderiza títulos, encabezados, listas con viñetas, bloques de código con fondo y texto normal con ajuste de línea
  - Desplazamiento vertical con flechas ↑↓ o rueda del ratón
- **Barra inferior**: atajos de teclado a la izquierda y acción actual de la animación a la derecha (amarillo)

### Estructuras de datos implementadas

| Estructura | Acciones animadas |
|---|---|
| **Array / Lista** | Recorrido por índice, búsqueda lineal, inserción, eliminación |
| **Linked List** | Recorrido de nodos, inserción al inicio, inserción al final, eliminación |
| **Doubly Linked List** | Recorrido adelante, recorrido atrás, inserción en medio, eliminación |
| **Deque** | Push front, Push rear, Pop front, Pop rear |
| **Stack / Pila** | Push (apilar), Peek (consultar tope), Pop (desapilar), Push — tope arriba |
| **Stack (lista enlazada)** | Push en HEAD, Peek TOP=HEAD, Pop HEAD, Push |
| **Queue / Cola** | Enqueue (encolar), Peek (consultar frente), Dequeue (desencolar), Enqueue |
| **Queue (lista enlazada)** | Enqueue en TAIL, Peek FRONT=HEAD, Dequeue HEAD, Enqueue |
| **Trie** | Insertar CAT, insertar CAR (prefijo), buscar prefijo CA, eliminar CAT |
| **AVL Tree** | Insertar con desbalance LL, rotación derecha, desbalance RR, rotación izquierda |
| **Union-Find** | Find raíz, Union de conjuntos, Union adicional, path compression |
| **Hash Set** | Add, Contains, Remove, Intersección |
| **Hash Map / Diccionario** | Inserción con colisión, búsqueda por clave, inserción en nuevo bucket, eliminación |
| **Binary Tree** | Recorridos preorden, inorden, postorden e inserción en BST |
| **Heap / Montículo** | Inserción con bubble-up, extracción con bubble-down, Peek (mínimo), Heapify |
| **Grafo** | BFS (anchura), DFS (profundidad), agregar vértice, agregar arista |

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
| `Rueda ratón` | Desplazar panel de información |

### Archivos de datos

Cada estructura de datos tiene su propio archivo `.md` en `src/ds_visualizer/data/` con la siguiente estructura:
1. Título (`#`)
2. Principales Características (`##`)
3. Elementos que la Componen (`##`)
4. Casos de Uso (`##`)
5. Pseudocódigo (`##` con bloques de código)
