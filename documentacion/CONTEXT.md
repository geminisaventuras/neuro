# @build: 2026-07-06.11-00-00 | id: DOC-004 | desc: Contexto del proyecto – arquitectura, modelo de datos y principios
# CONTEXT – Neuro-Swarm v5.0

## Visión general
Centro de mando multi-IAs con enrutamiento automático, memoria RAG multinivel y cifrado Zero‑Trust.

## Arquitectura de componentes

### Núcleo (core/)
- **database.py**: SQLite + Fernet. Tablas: `global_agents`, `project_agents`, `rag_contexts`, `documents`, `sessions`, `messages`.
- **orchestrator.py**: Itera agentes, inyecta contexto RAG (global, proyecto, agente, grupo), captura razonamiento, aplica degradación (1 fallo → amarillo, 2 → rojo, switch al siguiente).
- **code_executor.py**: Sandbox sin red y con lista blanca de imports.
- **sync_github.py**: Explorador de repositorios.

### Interfaz (gui/)
- **main.py**: Ensambla ventana, pestañas, cabecera. Verifica agentes al iniciar, atajos `Ctrl+←/→/↑`.
- **chat_frame.py**: Campo flotante, popover del selector, adjuntar, exportar MD, detener.
- **widgets.py**: NodeButton (semáforo + bombillito azul), UserBubble, ThinkingBlock, IAResponse, IterationMarker.
- **sidebar.py**: Historial con tiempo relativo y búsqueda profunda en mensajes.
- **toolbox.py**: Pestañas Docs, Prompts, Git, Dash con refresco seguro.
- **dialogs.py**: CRUD de agentes, calificación, guardar prompt.

## Modelo de datos simplificado
projects 1──* project_agents ──1 global_agents
sessions 1── messages
documents (independiente)
rag_contexts (level: global|project|agent|group)
agent_groups 1──* group_members *──1 global_agents

text

## Principios de diseño
- **Zero‑Trust**: Claves cifradas, validación en frontend y backend.
- **Aislamiento hermético**: Módulos sin estado global.
- **Agnosticismo tecnológico**: Interfaz desacoplada de proveedores.
- **Determinismo categórico**: Ante ambigüedad, preguntar al Operador.
