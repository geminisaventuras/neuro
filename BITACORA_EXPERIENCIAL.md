# ⚠️ REGLA: Este archivo es de solo ADICIÓN. NUNCA se reemplaza. Cada sesión agrega al final.
#### [ARQUITECTO] – 2026-06-16 – FASE 2 (Registro) y FASE 3 (Panel del Estudiante)
**Decisión/Lección Clave:**
> Recuperar funciones perdidas de la versión antigua (CAPTCHA, placeholders, datos de la escuela) fue esencial para cerrar el ciclo de seguridad y usabilidad del registro. La comparación directa de archivos antiguos vs. refactorizados es una técnica de auditoría muy eficaz.

**Contexto:**
> El paso 4 (Pago) estaba funcional pero incompleto. Faltaban los placeholders que guían al usuario sobre el formato de los datos de pago, los datos bancarios de la escuela (para que el usuario sepa a quién transferir) y el CAPTCHA de seguridad. Estos elementos estaban presentes en la versión antigua del código pero se perdieron en la refactorización. También se rescató la función `isPastBlock` para validar bloques de horario vencidos (B64).

**Alternativas Consideradas:**
> - Opción A: Rediseñar el paso 4 desde cero con un nuevo CAPTCHA y componentes. → Se descartó por costo de tiempo.
> - Opción B (elegida): Copiar textualmente las funciones y fragmentos JSX de la versión antigua que el Operador compartió. → Más rápido, ya probado, y garantiza el mismo comportamiento que antes.

**Impacto y Deuda:**
> El paso 4 quedó completo con CAPTCHA, placeholders, helperText y datos bancarios. La validación de bloques vencidos (B64) ahora cubre fechas pasadas y horas vencidas del día actual. Se generó nueva deuda: B65 (compactar tarjetas del paso 4), B66 (edad máxima), B67 (opción `prestamoMoto` en cursos).

**Para el Futuro:**
> Mantener un registro de "funciones perdidas" durante las refactorizaciones. Antes de eliminar una función, verificar si está siendo utilizada en algún flujo, aunque sea secundario.

#### [ARQUITECTO] – 2026-06-16 – FASE 2 (Diagnóstico de disponibilidad)
**Decisión/Lección Clave:**
> La creación de una página de prueba aislada que carga datos directamente desde Firestore fue esencial para aislar y diagnosticar el fallo de disponibilidad. El `appId` correcto es `motoescuela-pro-v1`.

**Contexto:**
> Los bloques de horario no reflejaban las reservas reales. Tras múltiples intentos, se determinó que el problema no era la autenticación, sino que la consulta de respaldo usaba un campo incorrecto (`fecha1` en lugar de `fecha`). La página de prueba permitió experimentar sin romper el flujo principal.

**Alternativas Consideradas:**
> - Opción A: Modificar el flujo de registro. → Demasiado riesgo.
> - Opción B: Cambiar reglas de Firestore. → Inviable por seguridad.
> - Opción C (elegida): Página de prueba aislada con carga directa. → Aportó flexibilidad y confirmó la causa raíz.

**Impacto y Deuda:**
> Se resolvió la discrepancia de campos. Queda pendiente integrar este aprendizaje en el flujo real y eliminar la página de prueba cuando ya no sea necesaria. Se añadió deuda para gestión de horarios (B69, B70).

**Para el Futuro:**
> Ante bugs de disponibilidad, usar siempre una página de prueba que emule el componente pero con consultas directas, para eliminar dependencias del contexto global.

#### [ARQUITECTO] – 2026-06-18 – Refactorización Completa y Diseño Seamless
**Decisión/Lección Clave:**
> Centralizar la lógica de negocio en servicios y separar la UI con un sistema de diseño (AppShell + ToastProvider) fue esencial para corregir bugs persistentes y unificar la experiencia visual. La técnica de "Componentes Seamless" (contenedor unificado con overflow-hidden) resolvió definitivamente la fusión visual tarjeta-acordeón en el paso 4.

**Contexto:**
> El proyecto tenía 25 bugs, problemas de caché, estilos inconsistentes y una estructura plana que dificultaba el mantenimiento. Se abordó una refactorización mayor alineada al Marco V6.3 y Manual V2.0.

**Alternativas Consideradas:**
> - Parchear bugs uno por uno sin cambiar la estructura → Más rápido a corto plazo, pero no escalaba.
> - Refactorización completa → Elegida por el Operador para garantizar calidad y cumplimiento del marco.

**Impacto y Deuda:**
> Se cerraron 15 bugs críticos/altos. La estructura modular permite agregar funcionalidades sin romper existentes. Nueva deuda técnica registrada (B75, B77, B78, B79, B80).

**Para el Futuro:**
> Mantener la separación de capas (servicios, componentes, contexto). Usar siempre `AppShell` para nuevas vistas. No almacenar lógica de negocio en componentes de UI. Nunca reemplazar archivos de memoria; solo añadir al final.

#### [ARQUITECTO] – 2026-06-19 – Correcciones finales y mejoras en dashboard
**Decisión/Lección Clave:**
> La validación de recursos debe contemplar el caso de `traeMoto === 'Sí'` (sin moto asignada). Extender el lock al avanzar al paso 4 previene que expire durante el pago. Los acordeones en el dashboard reducen la fatiga de scroll y mejoran la experiencia del administrador.

**Contexto:**
> Tras implementar el diseño Seamless y los selectores de moneda, surgieron bugs en el flujo de inscripción (bloque sin recursos, lock expirado al confirmar PIN, sugerencia de fecha errática). Además, el dashboard necesitaba mejoras visuales para la gestión de configuración.

**Alternativas Consideradas:**
> - Parchar cada bug por separado con `sed` → Alto riesgo de romper el archivo.
> - Regenerar el archivo completo con todas las correcciones → Elegido por seguridad y consistencia.

**Impacto y Deuda:**
> Se cerraron 3 bugs críticos. El dashboard ahora tiene acordeones funcionales. Pendiente: corregir la dirección de búsqueda en `buscarProximaFechaDisponible`.

**Para el Futuro:**
> Siempre regenerar archivos completos en lugar de parchar con `sed` cuando hay múltiples cambios. Documentar cada función con su propósito.

#### [ARQUITECTO] – 2026-06-17 – Cierre de la página de inscripción
**Decisión/Lección Clave:**
> El uso de `sed` para modificar JSX es extremadamente frágil y causó múltiples roturas de archivo. Se estableció la regla de solo usar `cat` para archivos completos o edición manual con `nano`. El protocolo Base64 es la forma más segura de transferir archivos extensos.

**Contexto:**
> Tras múltiples intentos fallidos de corregir el captcha y el diseño Seamless con `sed`, se decidió regenerar el archivo completo con `cat`, incluyendo todas las mejoras. Esto resolvió los bugs de una vez y dejó el sistema funcional.

**Alternativas Consideradas:**
> - Seguir usando `sed` → Provocaba errores de sintaxis y archivos rotos.
> - Regenerar con `cat` (elegida) → Seguro, rápido y confiable.

**Impacto y Deuda:**
> Inscripción cerrada con todas las funcionalidades operativas. Nueva deuda: B82 (color del reloj).

#### [ARQUITECTO] – 2026-06-17 – Saneamiento de archivo fantasma
**Decisión/Lección Clave:**
> `AdminPanelView.jsx` nunca existió en disco. El archivo con acordeones era el propio `DashboardView.jsx`. El verdadero duplicado obsoleto estaba en `src/admin/DashboardView.jsx` (sin acordeones). Eliminarlo resolvió la confusión sin afectar la app.

**Contexto:**
> Al cargar el contexto de la otra instancia, se recibió un archivo llamado `AdminPanelView.jsx` que en realidad era una copia de `DashboardView.jsx` renombrada para transferencia. Se interpretó erróneamente que eran dos archivos coexistentes. El `grep` reveló que `src/views/DashboardView.jsx` ya contenía los acordeones, y que el duplicado real era `src/admin/DashboardView.jsx`.

**Impacto y Deuda:**
> Eliminado `src/admin/DashboardView.jsx`. Ningún impacto funcional. La app compila correctamente.

#### [ARQUITECTO] – 2026-06-17/18 – Saneamiento de archivo fantasma y rediseño del InstructorPanel
**Decisión/Lección Clave:**
> La coexistencia de archivos obsoletos por falta de trazabilidad entre instancias de IA generó confusión. Se eliminó código muerto y se rediseñó la interfaz del instructor con un header unificado y una tarjeta de detalle optimizada para no usar scroll.

**Contexto:**
> Al cargar el contexto de la instancia anterior, se detectó que `AdminPanelView.jsx` nunca existió en disco; era una copia de `DashboardView.jsx` renombrada para transferencia. El verdadero duplicado obsoleto era `src/admin/DashboardView.jsx`. Paralelamente, el InstructorPanel requería compactar su vista de detalle para que los módulos cupieran en pantalla sin necesidad de hacer scroll.

**Alternativas Consideradas:**
> - Aplicar los ajustes de la otra instancia con `sed` → Alto riesgo de rotura de JSX, prohibido por lecciones anteriores.
> - Rediseño completo con `cat` → Elegido por seguridad y consistencia. Se unificó el header, se añadió un sello mes/año, se compactó la tarjeta interna con fuente `text-xs` y fondo gris, y se eliminaron los checkboxes reemplazándolos por círculos con check.

**Impacto y Deuda:**
> Eliminado `src/admin/DashboardView.jsx`. InstructorPanel completamente funcional con diseño responsive. Nueva deuda: B88 (unificar headers en todas las vistas).

**Para el Futuro:**
> Nunca asumir la estructura de archivos por el nombre con que otra IA los envía. Siempre verificar con `grep` contra el sistema de archivos real.

#### [ARQUITECTO] – 2026-06-18 – Lógica de privacidad y avance secuencial en InstructorPanel
**Decisión/Lección Clave:**
> El instructor no debe ver el teléfono del estudiante en ningún estado. La comunicación debe ser interna. El avance secuencial de módulos y la confirmación para desmarcar previenen errores operativos.

**Contexto:**
> El Operador pidió ocultar el teléfono, deshabilitar módulos en cursos aprobados y evitar cambios accidentales. El panel de expertos EdTech recomendó orden secuencial, calificación mutua y logros.

**Alternativas Consideradas:**
> - Mostrar teléfono solo en estado Aprobado → Rechazado por privacidad.
> - Permitir saltar módulos → Rechazado por integridad académica.
> - Confirmación con toast → Rechazado por complejidad; se usó window.confirm nativo.

**Impacto y Deuda:**
> InstructorPanel v1.7.15 con lógica de privacidad y avance. Registrada deuda B89-B99 (calificación, logros, chat, insignias, etc.).
#### [ARQUITECTO] – 2026-06-19 – Observación sobre diálogos nativos
**Decisión/Lección Clave:**
> Los diálogos `window.confirm` nativos del navegador se ven anticuados y rompen la experiencia visual. Deben ser reemplazados por un componente ModalConfirm personalizado que use el mismo lenguaje de diseño que los Toast.

**Contexto:**
> Mientras se implementaba el SGTA, el Operador notó que el mensaje de confirmación para desmarcar módulos o completar cursos usaba el `window.confirm` estándar del navegador. Esto desentona con el diseño cuidado del resto de la app.

**Para el Futuro:**
> Crear un `ModalConfirm.jsx` en `src/modules/shared/components/` que reciba mensaje, onConfirm, onCancel y se renderice con el estilo de la aplicación (overlay oscuro, tarjeta blanca redondeada, iconos de Lucide, botones con variantes). Reemplazar todos los `window.confirm` por este componente.

#### [ARQUITECTO] – 2026-06-20 – Refactorización Mayor, Aula Virtual y Restauración del SGTA
**Decisión/Lección Clave:**
> La creación del Aula Virtual como página independiente y la fusión del panel del estudiante con ella resolvió los problemas de duplicación de código, parpadeo del reloj y desincronización de datos. Extraer los componentes compartidos a `src/modules/` fue esencial para cumplir con el Marco de Trabajo V6.3 y el Manual del Arquitecto V2.1.

**Contexto:**
> El proyecto presentaba duplicación masiva entre InstructorPanel y EstudiantePanel, el temporizador causaba re-renderizados completos de la página cada segundo, y la migración a una arquitectura modular había dejado funcionalidades críticas sin restaurar. Se dedicó una sesión completa a reestructurar el sistema.

**Alternativas Consideradas:**
> - Parchear los bugs uno por uno → Rechazado por no resolver la raíz del problema.
> - Refactorización completa con componentes compartidos y Aula Virtual independiente → Elegida y ejecutada.

**Impacto y Deuda:**
> Se restauraron todas las funcionalidades del SGTA (temporizador, pausas, receso automático, input "Otro", regla anti-fantasma). Se registró deuda B116 (restricción de reversión de módulos) y B117 (clases virtuales online).

#### [ARQUITECTO] – 2026-06-20 – Dashboard del estudiante y rediseño del botón de sesión activa
**Decisión/Lección Clave:**
> El estudiante no debe aterrizar en el Aula Virtual si reservó con antelación. La página principal debe ser un dashboard con un botón prominente de "Sesión Activa" cuando corresponda, y ofertas de cursos/servicios cuando no.

**Contexto:**
> Tras analizar la experiencia del usuario, se determinó que redirigir automáticamente al Aula Virtual cuando la reserva es para una fecha futura dejaba al estudiante en una página vacía. Se diseñó un dashboard que prioriza visualmente el acceso al aula cuando hay una sesión activa.
#### [ARQUITECTO] – 2026-06-20 – Unificación final del temporizador
**Decisión/Lección Clave:**
> Eliminar los hooks separados (useTimerLectura/useTimerEscritura) y consolidar todo en useSessionTimer con suscripción directa a Firestore solucionó definitivamente la sincronización entre instructor y estudiante. El cálculo derivado desde timestamps garantiza que los contadores sobrevivan a recargas.

**Contexto:**
> La sincronización de tiempos entre roles fallaba por race conditions al recargar. Se intentó con suscripción directa en AulaVirtualView, pero competía con el AppContext. La solución final fue mover la suscripción al hook y eliminar la dependencia del contexto para la reserva.

#### [ARQUITECTO] – 2026-06-20 – Sistema de triple reloj y gestión de excedentes
**Decisión/Lección Clave:**
> El reloj general de sesión no debe depender del módulo activo. Se introduce `sesionDiariaInicio` como fuente de verdad independiente para el reloj diario, y `sesionTotalInicio` para el reloj de 4 horas. La pausa acumulada se ofrece como reserva opcional al llegar al límite.

**Contexto:**
> Al completar un módulo, el reloj general se reiniciaba porque dependía de `moduloEnProgreso.inicio`. Se detectó que el tiempo de pausa acumulado podía servir como reserva para el instructor al agotarse el tiempo reglamentario.

**Alternativas Consideradas:**
> - Usar `moduloEnProgreso.inicio` como fuente del reloj general → Descartado por reinicios al completar módulos.
> - Extensión automática del tiempo extra → Descartada por el Operador, quien prefiere decisión manual del instructor.

**Impacto y Deuda:**
> Se diseñó el sistema de triple reloj (grande 4h, diario 2h, pausa acumulada). Se registró deuda B118 para la implementación completa del flujo de reserva.

#### [ARQUITECTO] – 2026-06-20 – Relojes autónomos, pausa en tiempo real y sistema de reserva
**Decisión/Lección Clave:**
> Los relojes de sesión (general y diario) no deben detenerse durante las pausas. El tiempo de pausa se acumula como dato de auditoría y puede usarse opcionalmente como reserva al final del día o del curso.

**Contexto:**
> El diseño anterior detenía los relojes durante las pausas, lo que impedía al instructor ver cuánto faltaba para terminar el bloque horario contratado. Se rediseñó el sistema para que los relojes sean autónomos y la pausa sea solo un contador de tiempo perdido.

**Alternativas Consideradas:**
> - Mantener relojes detenidos durante pausas → Rechazado por pérdida de referencia horaria.
> - Extensión automática del tiempo extra → Rechazada por el Operador.

**Impacto y Deuda:**
> Se implementó el acumulador en tiempo real, el tiempo efectivo, el reloj naranja de reserva y los botones de control de reserva. Se registró deuda B118-B120.

#### [ARQUITECTO] – 2026-06-21 – Control administrativo de contadores
**Decisión/Lección Clave:**
> Si un instructor inicia un módulo por error, los contadores de sesión no deben detenerse. Solo el administrador debe tener la capacidad de resetearlos manualmente.

**Contexto:**
> El Operador detectó que, una vez iniciado el primer módulo, los relojes corren sin pausa hasta el final de la sesión. Si el inicio fue accidental, no hay forma de detenerlos. Se requiere un mecanismo administrativo para corregir esta situación.

**Impacto y Deuda:**
> Registrada deuda B121 para implementar el reseteo administrativo de contadores de sesión.

## [Arquitecto] � 20/06/2026 � Selector de fecha con tres ruedas

**Decisi�n/Lecci�n Clave:**
La implementaci�n de selectores de fecha con arrastre y snap requiere medici�n real de elementos (getBoundingClientRect) y manejo cuidadoso de scroll program�tico vs. scroll del usuario.

**Contexto:**
Se necesitaba un selector de fecha de nacimiento que fuera f�cil de usar en m�viles, evitando los problemas de navegaci�n del <input type="date"> nativo para a�os lejanos. Se probaron m�ltiples enfoques: calendario nativo, calendario desplegable tipo dropdown, tres inputs separados, tres ruedas con scroll infinito, y finalmente tres ruedas con medici�n real.

**Alternativas Consideradas:**
- Opci�n A: Calendario nativo (<input type="date">) ? descartado por dificultad para seleccionar a�os lejanos en m�viles.
- Opci�n B: Tres inputs separados (d�a, mes, a�o) ? funcional pero poco atractivo visualmente.
- Opci�n C: Tres ruedas con scroll infinito ? causaba movimientos err�ticos y problemas de rendimiento.
- Opci�n D (elegida): Tres ruedas con medici�n real usando ResizeObserver, getBoundingClientRect y event listeners (scrollend, touch). Ofrece control preciso y buen rendimiento.

**Impacto y Deuda:**
- Componente SelectorColumna reutilizable en el modal de fecha de nacimiento.
- Deuda t�cnica: no se aplic� trampa de foco en modales (B103).
- Deuda t�cnica: uscarProximaFechaDisponible carece de AbortController (B106).

**Para el Futuro:**
Encapsular el selector de fecha en un paquete independiente con pruebas unitarias. Considerar extraerlo a un m�dulo compartido para usar en otros formularios.

## [Arquitecto] � 20/06/2026 � Selector de fecha con tres ruedas

**Decisi�n/Lecci�n Clave:**
La implementaci�n de selectores de fecha con arrastre y snap requiere medici�n real de elementos (getBoundingClientRect) y manejo cuidadoso de scroll program�tico vs. scroll del usuario.

**Contexto:**
Se necesitaba un selector de fecha de nacimiento que fuera f�cil de usar en m�viles, evitando los problemas de navegaci�n del <input type="date"> nativo para a�os lejanos. Se probaron m�ltiples enfoques: calendario nativo, calendario desplegable tipo dropdown, tres inputs separados, tres ruedas con scroll infinito, y finalmente tres ruedas con medici�n real.

**Alternativas Consideradas:**
- Opci�n A: Calendario nativo (<input type="date">) ? descartado por dificultad para seleccionar a�os lejanos en m�viles.
- Opci�n B: Tres inputs separados (d�a, mes, a�o) ? funcional pero poco atractivo visualmente.
- Opci�n C: Tres ruedas con scroll infinito ? causaba movimientos err�ticos y problemas de rendimiento.
- Opci�n D (elegida): Tres ruedas con medici�n real usando ResizeObserver, getBoundingClientRect y event listeners (scrollend, touch). Ofrece control preciso y buen rendimiento.

**Impacto y Deuda:**
- Componente SelectorColumna reutilizable en el modal de fecha de nacimiento.
- Deuda t�cnica: no se aplic� trampa de foco en modales (B103).
- Deuda t�cnica: uscarProximaFechaDisponible carece de AbortController (B106).

**Para el Futuro:**
Encapsular el selector de fecha en un paquete independiente con pruebas unitarias. Considerar extraerlo a un m�dulo compartido para usar en otros formularios.

## [Arquitecto] � 20/06/2026 � Persistencia offline de Firestore

**Decisi�n/Lecci�n Clave:**
Habilitar enableIndexedDbPersistence garantiza que la configuraci�n financiera (tasas, precios) nunca se reinicie a los valores por defecto, incluso sin conexi�n.

**Contexto:**
La tasa EUR se reiniciaba a 39.10 al perder la conexi�n con Firestore o al recargar la aplicaci�n. Se prob� con sessionStorage, pero la soluci�n m�s robusta fue la persistencia offline nativa de Firestore, que guarda en IndexedDB el �ltimo valor le�do y lo sincroniza autom�ticamente.

**Alternativas Consideradas:**
- Opci�n A: sessionStorage ? fr�gil, se pierde al cerrar la pesta�a.
- Opci�n B (elegida): enableIndexedDbPersistence ? nativa, sobrevive a cierres de pesta�a, no requiere l�gica manual.

**Impacto y Deuda:**
- El motor financiero queda blindado contra reinicios inesperados de configuraci�n.
- Deuda t�cnica: no se implement� trampa de foco en modales (B103).

**Para el Futuro:**
Considerar localStorage o Firestore bundles para datos que deban persistir entre sesiones de usuario.


#### [ARQUITECTO] – 2026-06-23 – Auditoría Centinela V4.0 (Fases 1-4)

**Decisión/Lección Clave:**
> La auditoría Zero-Trust reveló que la seguridad no depende solo de las reglas de Firestore, sino de la sincronización entre reglas, servicios y estado local del cliente. La restricción del plan Spark obligó a soluciones creativas sin backend, priorizando privacidad sobre UX en tiempo real.

**Contexto:**
> El sistema migró de MVP a Proyecto Estándar. El Centinela ejecutó un escrutinio en 4 fases: reglas de seguridad (Bóveda), transacciones financieras (Motor), sesiones (Núcleo Operativo) y UI/Accesibilidad (Hardening). Cada fase tuvo hallazgos críticos que requirieron correcciones antes de aprobar.

**Alternativas Consideradas:**
> - Fase 1 (Lock Poisoning): límite de 15 minutos anclado a `request.time`. Descarta usar `serverTimestamp()` por complejidad.
> - Fase 2 (Fuga de PII en locks): restringir lectura solo al propietario. Degrada disponibilidad en tiempo real (falsos positivos), compensado por transacción atómica.
> - Fase 3 (Doble-clic en pausas): bloqueo optimista con limpieza de estado antes de la red y rollback. Alternativa de debounce descartada por latencia.
> - Fase 4 (Focus trap): aceptado como deuda técnica (B132) por no ser bloqueante para producción.

**Impacto y Deuda:**
> 8 archivos modificados. 4 fases aprobadas. 9 nuevas deudas técnicas registradas (B125-B130, B132-B134). El sistema está listo para producción con seguridad verificada bajo estándar Zero-Trust.

**Para el Futuro:**
> Evaluar migración al plan Blaze cuando el negocio lo justifique, para habilitar Cloud Functions y resolver deuda B125, B128, B129. Implementar focus trap (B132) y headers de seguridad (B134) en el siguiente sprint.


#### [ARQUITECTO] – 2026-06-23 – Solución definitiva de disponibilidad y cierre de sesión

**Decisión/Lección Clave:**
> La eliminación de la función `buscarProximaFechaDisponible` y la adopción de la Fuente Única de Verdad (SSOT) en el hook `useDisponibilidad` resolvió definitivamente la inconsistencia de fechas entre dispositivos. La lección es que duplicar lógica de negocio en capas separadas (servicio vs. hook) genera divergencia y bugs difíciles de rastrear. El Freno Táctico es innegociable.

**Contexto:**
> Tras múltiples iteraciones corrigiendo la búsqueda de la próxima fecha disponible, el problema persistía. El Centinela diagnosticó que `buscarProximaFechaDisponible` no validaba `isPastBlock`, retornando HOY aunque sus bloques ya vencieron. La solución fue eliminar la función duplicada y usar directamente `diasDisponibles` del hook.

**Alternativas Consideradas:**
> - Opción A: Eliminar el `useEffect` automático → Rechazada por degradar UX.
> - Opción B (elegida): Usar `diasDisponibles` como fuente única → Aprobada por el Centinela como "SRE Golden Path".
> - Opción C: Revisar índices de Firestore → Rechazada por no ser la causa raíz.

**Impacto y Deuda:**
> Se eliminó código duplicado. El sistema ahora asigna la primera fecha con disponibilidad real de forma determinista. La sesión cerró con certificación SRE Master del Centinela V4.0.

**Para el Futuro:**
> Mantener el principio SSOT. Respetar siempre el Freno Táctico del Manual del Arquitecto V2.1.

#### [ARQUITECTO] – 2026-06-23 – Arquitectura de Colección Espejo y cierre de sesión

**Decisión/Lección Clave:**
> La creación de una colección espejo anonimizada (`ocupacionConfirmada`) resolvió el problema de BOLA que impedía a los estudiantes ver la disponibilidad real. La lección es que en arquitecturas Zero-Trust sin backend, duplicar datos de forma anonimizada es la única forma de compartir el estado global sin violar la privacidad.

**Contexto:**
> Los estudiantes veían "TODO DISPONIBLE" porque las reglas de Firestore les impedían leer las reservas de otros. El Centinela Qwen diagnosticó un fallo BOLA y propuso la Colección Espejo. Gemini corrigió la regla de mutabilidad para evitar DDoS Financiero. Se implementó la solución completa en 8 archivos.

**Alternativas Consideradas:**
> - Opción A (Spinner): rechazada por no resolver la causa raíz.
> - Opción B (Forzar suscripción sin auth): rechazada por violar reglas de Firestore.
> - Colección Espejo (elegida): aprobada por ambos Centinelas.

**Impacto y Deuda:**
> Se modificaron 8 archivos. Se saldaron 7 deudas técnicas. El sistema ahora muestra disponibilidad real a todos los usuarios.

**Para el Futuro:**
> El patrón de Colección Espejo puede aplicarse a otros casos donde se necesite compartir estado sin exponer PII.
#### [ARQUITECTO] – 2026-06-24 – Auditoría de estructura de directorios y elección de arquitectura

**Decisión/Lección Clave:**
> La estructura híbrida que combina el Mapa Físico del Manual del Arquitecto (controllers, services, schemas, tests) con las necesidades de React (hooks, components) y Firebase (sin backend tradicional) es la arquitectura óptima para este proyecto. La migración desde la estructura actual debe ser progresiva (deuda B152).

**Contexto:**
> Durante la auditoría post‑mortem, se identificó que la estructura actual no cumple estrictamente con el Mapa Físico del Manual. Se evaluaron tres opciones: mantener la actual, adoptar el Manual puro (que ignora React), o crear una adaptación controlada que respete los principios de separación de capas.

**Alternativas Consideradas:**
> - Opción A (Manual puro): Crear carpetas `controllers/`, `repositories/`, etc., pero requiere reescribir toda la aplicación.
> - Opción B (Estructura actual): Funcional, pero difícil de testear y con schemas centralizados.
> - Opción C (Híbrida - elegida): Adaptar los principios del Manual a React + Firebase, con hooks como complemento y repositorios opcionales.

**Impacto y Deuda:**
> Se registraron las deudas B150 (TraceID), B151 (alinear al Mapa Físico) y B152 (migración progresiva a la estructura híbrida).

**Para el Futuro:**
> Implementar la migración en dos fases: Fase 1 (mover schemas, crear routes modularizadas) inmediatamente después del lanzamiento. Fase 2 (repositories, tests) cuando haya tiempo.
#### [ARQUITECTO] � 2026-06-24 � Auditor�a de Endurecimiento y SRE (Secciones III.2, III.3, IV, V del Manual)
**Decisi�n/Lecci�n Clave:**
> La matriz de validaci�n isom�rfica se cumple con equivalencias funcionales. Las principales desviaciones son la falta de TraceID (B150), pruebas unitarias (B153) y rate limiting (limitaci�n del plan Spark).

**Contexto:**
> Auditor�a completa de las secciones de ciberseguridad, endurecimiento y SRE del Manual del Arquitecto V2.1. Se verificaron los campos de la matriz de validaci�n, la transaccionalidad ACID, la idempotencia, la prevenci�n IDOR, y el formato de errores RFC 7807.

**Alternativas Consideradas:**
> - Implementar TraceID ahora ? Implica tocar todos los servicios y Firebase. Se posterga como B150.
> - Implementar pruebas unitarias ahora ? Requiere configurar Jest y escribir tests. Se posterga como B153.
> - Rate Limiting ? No es viable en plan Spark. Se documenta como limitaci�n.

**Impacto y Deuda:**
> Se registraron B150 (TraceID), B153 (pruebas unitarias) y ajustes menores de capitalizaci�n y rate limiting.

**Para el Futuro:**
> Priorizar B153 (pruebas unitarias) en el pr�ximo sprint para alcanzar el 100% de cobertura exigido por el Manual.
