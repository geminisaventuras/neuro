# @build: 2026-07-06.10-00-00 | id: DOC-003 | desc: Backlog de deudas técnicas y funcionalidades pendientes
# TECHNICAL_DEBT – Neuro-Swarm v5.0

## Funcionalidades pendientes (prioridad alta)
| ID | Descripción | Complejidad | Estado |
|----|-------------|-------------|--------|
| T001 | Implementar contenido de la pestaña Dashboard Analítico | Media | Pendiente |
| T002 | Implementar contenido de la pestaña Contexto RAG (edición multinivel con archivos) | Alta | Pendiente |
| T003 | Implementar contenido de la pestaña Sincronización (GitHub) | Media | Pendiente |
| T004 | Gestión de grupos de IAs con interfaz gráfica | Alta | Pendiente |
| T005 | Auto-guardado de sesión al cerrar la aplicación | Baja | Pendiente |

## Mejoras de UX (prioridad media)
| ID | Descripción | Complejidad | Estado |
|----|-------------|-------------|--------|
| T006 | Colapso de paneles con animación suave (deslizamiento) | Media | Pendiente |
| T007 | Indicador de progreso en ThinkingBlock (contador de segundos o animación) | Baja | Pendiente |
| T008 | Rayitas de índice laterales (como DeepSeek) | Baja | Pendiente |
| T009 | Búsqueda con debounce en el historial para no sobrecargar | Baja | Pendiente |
| T010 | Campo de búsqueda que también busque en el contenido completo de sesiones antiguas (ya implementado parcialmente) | Hecho | Verificado |

## Bugs conocidos
| ID | Descripción | Prioridad | Estado |
|----|-------------|-----------|--------|
| B001 | Algunos agentes quedan en gris tras la verificación inicial (timeout corto) | Media | Pendiente |
| B002 | El botón de exportar no incluye los mensajes del sistema en el Markdown | Baja | Pendiente |
| B003 | La pestaña Git de la toolbox muestra "Conectado" aunque no se haya configurado token | Baja | Pendiente |
| B004 | Al cambiar de proyecto, el agente seleccionado no se limpia (bombillito azul permanece) | Baja | Pendiente |
