# @build: 2026-07-06.10-30-00 | id: DOC-001 | desc: Arranque de memoria completo – desde el día 0 hasta la v5.0
# MEMORY_BOOT – Neuro-Swarm v5.0

> **Propósito:** Este documento es la memoria persistente del proyecto. Al inicio de cada sesión, se inyecta como contexto para que cualquier IA (incluido el Arquitecto Koby) recuerde instantáneamente qué es Neuro‑Swarm, cómo se construyó, qué decisiones se tomaron, qué errores se cometieron y qué deudas técnicas existen.

---

## 🧠 Capa 1 – Memoria Sensorial (Hot): Estado actual y arranque rápido
*(Lo que necesitas saber para empezar a trabajar AHORA)*

### Estructura de archivos
neuro-swarm/
├── core/
│ ├── database.py ← Persistencia cifrada, tablas, migraciones
│ ├── orchestrator.py ← Enrutamiento, RAG, cancelación, razonamiento nativo
│ ├── code_executor.py ← Sandbox aislado
│ └── sync_github.py ← GitHub Sync
├── gui/
│ ├── widgets.py ← NodeButton, UserBubble, ThinkingBlock, IAResponse
│ ├── chat_frame.py ← Chat completo con barra flotante, popover, exportación
│ ├── sidebar.py ← Historial con tiempo relativo y búsqueda profunda
│ ├── toolbox.py ← Panel derecho con Docs, Prompts, Git, Dash
│ └── dialogs.py ← Diálogos Agregar/Editar IA, Calificar, Guardar Prompt
├── documentacion/
│ ├── MEMORY_BOOT.md ← Este archivo
│ ├── EXPERIENCE_LOG.md ← Bitácora de errores y soluciones
│ ├── TECHNICAL_DEBT.md ← Backlog de pendientes
│ ├── CONTEXT.md ← Mapa mental de la arquitectura
│ └── openapi.yaml ← Especificación de la API unificada
└── main.py ← Punto de entrada (~250 líneas)

text

### Dependencias y arranque
```bash
pip install openai google-genai customtkinter httpx requests cryptography
python main.py
Proveedores configurados
GEMA (Gemini)

CEREBRAS (Cerebras)

GRONKA (Groq)

MANTRAX (Mistral)

FREESTAR / CERBROSS / MISK / GRAKO (OpenRouter)

📖 Capa 2 – Memoria de Trabajo (Warm): Sesión actual y decisiones recientes
(Lo que se construyó y decidió en la última sesión)

Mejoras implementadas (2026-07-05/06)
Separación modular de main.py (~900 líneas) en 7 módulos GUI.

Interfaz DeepSeek con campo flotante, burbujas asimétricas, ThinkingBlock colapsable.

Semáforos de agentes con verificación inicial y bombillito azul para seleccionado.

Popover del selector integrado en el input, con toggle y cierre por foco.

Exportación a Markdown del chat completo.

Captura de razonamiento nativo de APIs (Groq, OpenRouter, Gemini).

Detención inmediata del ThinkingBlock al cancelar generación.

Decisiones de diseño
Separación de agentes globales: Ya no dependen del proyecto; se asocian mediante project_agents.

RAG multinivel: Global, Proyecto, Agente y Grupo.

Zero-Trust: Claves cifradas con Fernet, sin confianza en el frontend.

Determinismo categórico: No asumir reglas de negocio; preguntar al Operador.

📚 Capa 3 – Memoria Episódica y Semántica (Cold): Historia completa del proyecto
(Cómo se construyó Neuro‑Swarm desde el día 0)

Día 0 – El inicio (2026-07-04)
El Operador presentó un bloque de código del SwarmOrchestrator con proveedores Groq, Mistral, Gemini y custom.

Primer error detectado: URL de Groq incorrecta (https://api.groq.com/v1 → https://api.groq.com/openai/v1).

Segundo error: El modelo llama3.1-8b en Cerebras no existía; se corrigió a llama-3.3-70b.

Se añadió el proveedor Cerebras como nativo.

Se integró OpenRouter con sus headers obligatorios (HTTP-Referer, X-Title).

Se corrigió el método get_node_key para aplicar strip() y eliminar saltos de línea invisibles en las API keys.

Día 1 – Expansión y madurez (2026-07-05)
Se añadió el sistema de semáforos para los agentes (verde, amarillo, rojo, gris).

Se implementó la cancelación de generación con CancelledException y threading.Event.

Se añadió el botón Stop y la lógica de switch automático entre agentes ante fallos.

Se integró la carga de archivos (documentos RAG) con botón de adjuntar.

Se añadió el panel de historial de sesiones con Sidebar.

Se añadió la caja de herramientas derecha (Toolbox).

Día 2 – Refactorización visual (2026-07-05/06)
Se rediseñó completamente la interfaz siguiendo el estilo DeepSeek.

Se crearon los componentes asimétricos: UserBubble (glass), IAResponse (sin contenedor), ThinkingBlock (colapsable).

Se añadió el popover del selector de IA dentro de la barra de entrada.

Se implementó la exportación a Markdown del chat.

Se añadió la captura de razonamiento nativo de las APIs.

Se corrigieron múltiples errores de Tcl, popover, inicialización de variables y detención de generación.

Hitos principales
Fecha	Hito
2026-07-04	Orquestador multi-proveedor funcional (Groq, Mistral, Gemini, Cerebras, OpenRouter)
2026-07-05	Sistema de semáforos, cancelación, carga de archivos, sesiones
2026-07-06	Interfaz DeepSeek, popover, exportación Markdown, razonamiento nativo
🧠 Capa 4 – Metacognición: Lecciones aprendidas y patrón de errores
(Aplicando los conceptos de MISK, GRAKO, GEMA, CERBROSS y FREESTAR)

Lecciones aprendidas (consolidadas)
CustomTkinter no soporta transparencia real. El efecto glass se simuló con fg_color="#1e1e1e" y border_color="#333333".

Siempre validar diccionarios antes de iterarlos. El error AttributeError: 'ChatFrame' object has no attribute 'agent_mapping' se resolvió inicializando el diccionario vacío.

Separar la UI en módulos pequeños facilita la depuración y evita tocar código que ya funciona.

La detención de una generación debe reflejarse inmediatamente en la UI. No se debe esperar a que el hilo termine.

Las APIs modernas ya ofrecen razonamiento estructurado (reasoning_content). Aprovecharlo mejora la trazabilidad.

El tiempo del Operador es el activo más valioso. No se deben generar archivos incompletos o rotos.

Errores recurrentes y sus soluciones
Error	Causa	Solución
TclError al refrescar toolbox	Destrucción de widgets internos de CTk	Reutilizar frames contenedores
API key con \n invisible	Copia/pegado defectuoso	strip() en get_agent_key()
Popover no cerraba al hacer clic fuera	FocusOut prematuro	Eliminar FocusOut, usar solo toggle
Agente siempre seleccionaba el mismo	agent_mapping no inicializado	Inicializar vacío y llamar después
ThinkingBlock colgado tras error	Sin else para success=False	Añadir else con limpieza
📋 Capa 5 – Metadatos cognitivos del proyecto
(Información sobre la propia memoria del sistema)

json
{
  "project_name": "Neuro-Swarm",
  "version": "5.0.0",
  "created": "2026-07-04",
  "last_updated": "2026-07-06",
  "total_files": 15,
  "total_lines": 4500,
  "confidence_score": 0.95,
  "source_origin": "pair_programming",
  "temporal_validity": "2026-12-31",
  "semantic_depth": "abstract",
  "tags": ["multi-agent", "rag", "zero-trust", "python", "customtkinter", "deepseek-ui"]
}
"No construyas un archivo; construye un colega que entienda lo que olvida." – FREESTAR
