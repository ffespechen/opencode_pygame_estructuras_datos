# ARCHITECTURE.md

## Decisiones de arquitectura y tomas de partido

### 1. Estructura del proyecto — layout `src/`

Se adoptó el layout `src/` (con `src/ds_visualizer/`) siguiendo las recomendaciones de la skill `python-project-structure`. Esto separa el código fuente del resto de artefactos (documentación, configuración) y evita importaciones accidentales del paquete sin instalarlo.

**Motivación**: proyectos con múltiples módulos se benefician de esta organización para evitar ambigüedades en `sys.path` y mantener clara la raíz del paquete.

### 2. Máquina de estados explícita (`states/`)

La aplicación alterna entre dos modos mutuamente excluyentes:

- **MenuState**: pantalla inicial de selección (9 opciones: 8 estructuras + "Salir")
- **VisualizationState**: pantalla dividida verticalmente con animación e información

Cada estado implementa una interfaz implícita con los métodos `on_enter()`, `on_resize()`, `handle_events()`, `update(dt)`, `draw(screen, w, h)`. La clase `App` en `app.py` actúa como orquestador y decide cuándo transicionar basándose en banderas (`selected_ds`, `back_to_menu`). La opción "Salir" usa la clave especial `"__quit__"` que `App` detecta y provoca `running = False`.

**Motivación**: patrón State del GoF simplificado. Evita condicionales anidados en el loop principal y permite que cada pantalla gestione sus propias interacciones de forma aislada.

### 3. Separación UI / lógica de animación

- **`ui/`**: componentes puros de renderizado sin estado de negocio
  - `InfoPanel`: parsea `.md` y pre-renderiza superficies con formato
  - `ShortcutsBar`: barra fija inferior con atajos y acción actual de la animación
- **`animations/`**: cada estructura de datos tiene su propia clase que hereda de `BaseAnimation`
  - `BaseAnimation` define `update(dt)`, `draw(surface, rect)` y `current_action`
  - Las animaciones gestionan un ciclo de 4 acciones con temporizador interno

**Motivación**: principio de responsabilidad única (SRP). Cambiar el formato de los atajos no debería afectar a las animaciones, y viceversa. Añadir una nueva estructura solo requiere crear un `.md` y una clase de animación en el directorio correspondiente, luego registrarla en el diccionario `ANIMATION_MAP`.

### 4. Parser de Markdown propio vs librería externa

Se implementó un parser de Markdown personalizado en `InfoPanel._parse_markdown()` en lugar de usar una librería como `markdown` o `mistune`.

**Motivación**:
- Los archivos `.md` tienen una estructura predecible y controlada (5 secciones fijas)
- Un parser externo añadiría una dependencia que solo se usa para 6 archivos pequeños y acotados
- Renderizar HTML de una librería en Pygame requeriría un paso intermedio costoso (HTML → Superficie)
- El parser propio permite control fino sobre estilos: color de acento para headers, fondo oscuro para código, viñetas personalizadas

### 5. Pre-renderizado vs renderizado por frame

El panel de información pre-renderiza todo el contenido a una `pygame.Surface` vertical completa y luego solo blitea la porción visible (scroll). No se re-renderiza cada frame.

**Motivación**: el contenido de texto no cambia durante la visualización. Pre-renderizar una vez y desplazar es significativamente más eficiente que recalcular wrapping y blitear texto cada frame (60 fps). Solo se re-renderiza al cambiar de estructura o al redimensionar la ventana.

### 6. Animaciones basadas en temporizador y progreso

Cada animación define una lista de tuplas `(nombre, duración)` donde `nombre` es la etiqueta que aparece en la barra inferior y `duración` son los segundos que dura la acción. `BaseAnimation.progress()` devuelve un valor en `[0, 1)` que las subclases usan para interpolar visualmente.

**Motivación**:
- Desacopla la velocidad de animación del framerate (delta-time independent)
- Facilita crear secuencias: la subclase solo consulta `self.progress()` y dibuja en función de ese valor
- Añadir una nueva acción es agregar una tupla a `self.actions`

### 7. Redimensionamiento adaptativo

- `App._handle_resize()` impone un tamaño mínimo de 800×600
- En `VisualizationState`, el layout vertical usa proporción fija: panel superior (animación) = 45%, panel inferior (texto) = 55% del alto de contenido
- `InfoPanel.load_markdown()` recibe el ancho y alto visibles y re-renderiza el contenido a ancho completo (`width - 2 * padding`)
- Las animaciones reciben un `pygame.Rect` y dibujan relativo a él (sin coordenadas absolutas)

**Motivación**: la aplicación debe ser usable en distintos tamaños de ventana. El enfoque de posicionamiento relativo evita coordenadas mágicas y facilita el soporte de resize.

### 8. Layout vertical en lugar de horizontal

Inicialmente la pantalla de visualización se dividía horizontalmente (panel izquierdo = texto, panel derecho = animación). Este diseño presentaba problemas: el texto tenía solo la mitad del ancho disponible y el clip rect del panel izquierdo podía interferir con la animación.

Se migró a un layout vertical:
- Sección superior (45%): animación a ancho completo
- Sección inferior (55%): texto markdown a ancho completo, scrollable
- Barra inferior: atajos de teclado

**Motivación**: el texto markdown se beneficia de mayor ancho (evita wrapping excesivo), la animación tiene más espacio horizontal, y la separación vertical elimina conflictos de clip rect entre paneles.

### 9. Archivos de datos externos (.md)

La información de cada estructura se almacena en archivos Markdown individuales en `src/ds_visualizer/data/`.

**Motivación**:
- Permite corregir, ampliar o traducir el contenido sin tocar el código Python
- Facilita contribuciones de personas no desarrolladoras (solo necesitan editar texto)
- Cada archivo es autocontenido y corresponde 1:1 con una estructura de datos

### 10. Animaciones de Hash Map y Heap

**Hash Map (`hash_map.py`)**: visualiza 7 buckets como columnas etiquetadas con índices. Muestra la función hash (`Σ ord(c) mod 7`) y cómo las claves se distribuyen en buckets. La colisión se representa mostrando dos pares clave-valor en el mismo bucket. La búsqueda resalta el bucket correspondiente y luego la clave encontrada. Los pares se muestran como texto `clave:valor` dentro de cada bucket.

**Heap (`heap.py`)**: representa el min-heap simultáneamente como árbol y como array. El árbol ocupa la parte superior y el array la barra inferior, ambos con los mismos valores sincronizados. Los nodos del árbol mantienen la propiedad de heap (padre ≤ hijos). La inserción muestra cómo un nuevo valor aparece al final del árbol y "flota" hacia arriba (bubble-up). La extracción intercambia raíz con último, elimina y aplica bubble-down. Heapify muestra un array desordenado transformándose progresivamente en heap.

### 11. Esquema de colores oscuro

Paleta basada en tonos azul oscuro con acentos cian y amarillo:

| Elemento | Color | Uso |
|---|---|---|
| `BG_COLOR` | `(18, 18, 28)` | Fondo principal |
| `PANEL_BG` | `(35, 42, 58)` | Fondo de paneles superior e inferior |
| `TEXT_COLOR` | `(220, 220, 230)` | Texto normal |
| `ACCENT_COLOR` | `(100, 200, 255)` | Títulos, bordes, selección |
| `HIGHLIGHT_COLOR` | `(255, 200, 50)` | Elementos resaltados, acción actual |
| `CODE_BG` | `(45, 48, 68)` | Fondo de bloques de código |
| `SHORTCUT_BG` | `(22, 22, 35)` | Barra inferior de atajos |

**Motivación**: tema oscuro para reducir fatiga visual en uso prolongado y mantener consistencia con entornos de desarrollo modernos. `PANEL_BG` se diferencia claramente de `BG_COLOR` (+17, +24, +30 en RGB) para que los paneles sean visibles.

### 11. Manejo del evento QUIT, Ctrl+Q y opción Salir

El cierre de la aplicación se captura de tres formas en `App.handle_events()`:
- `pygame.QUIT` (clic en X de la ventana) → `self.running = False`
- `KEYDOWN` con `K_q` + `KMOD_CTRL` → `self.running = False`
- Selección de la opción "Salir" (`"__quit__"`) en el menú → `self.running = False`

**Motivación**: manejo centralizado de salida con múltiples vías de acceso. Los estados no necesitan preocuparse por cómo cerrar la aplicación, solo por su propia lógica de navegación.

### 12. Opción Salir en el menú

La novena opción del menú (`"Salir"`, clave `"__quit__"`) permite cerrar la aplicación desde el propio menú sin usar `Ctrl+Q`. Se distingue visualmente:
- Línea divisoria horizontal encima separándola de las estructuras de datos
- Color atenuado (`SUBTEXT_COLOR`) cuando no está seleccionada
- Mismo resaltado azul que las demás opciones al estar seleccionada

**Motivación**: mejora la usabilidad ofreciendo una forma explícita y visible de salir, complementaria a los atajos de teclado.
