# @build: 2026-07-06.11-00-00 | id: DOC-002 | desc: Bitácora de experiencia – errores, soluciones y lecciones
# EXPERIENCE_LOG – Neuro-Swarm v5.0

## Sesión 2026-07-04 al 2026-07-06

### Logros principales
1. Orquestador multi-proveedor con enrutamiento estricto y switch automático ante fallos.
2. Interfaz DeepSeek modular (burbujas asimétricas, campo flotante, popover).
3. Semáforos de estado con verificación inicial y bombillito azul para el agente seleccionado.
4. Captura de razonamiento nativo de APIs y encapsulamiento en `ThinkingBlock`.
5. Exportación del chat a Markdown con formato de código.

### Tabla de fallos y soluciones
| Problema | Causa | Solución |
|----------|-------|----------|
| `TclError` al refrescar Toolbox | Destrucción y recreación de widgets internos de CTk | Reutilizar frames contenedores, solo destruir hijos |
| API key con salto de línea invisible | Copia con `\n` al final | Aplicar `.strip()` en `get_agent_key()` |
| Popover no cerraba al seleccionar IA | `FocusOut` destruía la ventana antes del comando | Eliminar `FocusOut`, usar solo toggle |
| Agente siempre seleccionaba el mismo | `_highlight_selected_agent` llamado antes de existir `agent_mapping` | Inicializar `agent_mapping = {}` y llamar después |
| ThinkingBlock colgado tras error del orquestador | Sin bloque `else` para `success=False` | Añadir `else` con `_remove_thinking()` y mensaje de error |

### Lecciones aprendidas
- CustomTkinter no soporta transparencia real; simular con bordes sutiles.
- Validar existencia de diccionarios antes de iterar.
- La UI debe reflejar la cancelación de inmediato, no esperar al hilo.
- Las APIs modernas exponen `reasoning_content`; aprovecharlo mejora trazabilidad.
- El tiempo del Operador es el activo más valioso: no entregar código roto o incompleto.
