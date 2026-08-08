# Cognitive Observatory — Roadmap por Fases

**Documento hermano:** `01_spec_proyecto.md` (arquitectura y decisiones de diseño completas)

## Cómo usar este documento con Claude Code

- Trabajá **una subfase a la vez**. No le pases "construime el proyecto" — pasale la subfase puntual, con su Definition of Done.
- Ninguna fase empieza hasta que la anterior cumple su Definition of Done. Si Claude Code propone adelantarse (ej. meter dashboard en Fase 2), es señal de scope creep — volver a este documento.
- Cada fase termina con **un resultado que se puede correr y mostrar**, no solo código escrito. Si una fase termina sin un output real (un JSON de métricas, un número, una gráfica), no está terminada.
- Cuando algo del `01_spec_proyecto.md` no está todavía en el roadmap (self-model, atención, dashboard...), es intencional — está en fases posteriores, no olvidado.

---

## Fase 0 — Esqueleto del repo

**Objetivo:** tener el proyecto instalable y testeable, sin lógica cognitiva todavía.

### 0.1 Estructura base
- Repo con `core/`, `environments/`, `agents/`, `metrics/`, `experiments/`, `tests/` (sin `dashboard/` todavía).
- `pyproject.toml`, entorno virtual, `pytest`, `ruff`, `mypy` configurados y corriendo (aunque sea sobre un test dummy).
- CLI mínimo: `cognitive-observatory --version`.

**Definition of Done:** `pytest` corre verde, `ruff check` y `mypy` no tiran error, el CLI responde.

---

## Fase 1 — Loop mínimo: World + Sensor + Agent 0 vs Agent 2

**Objetivo:** el ciclo completo OBSERVE → ACT funcionando de punta a punta, aunque sea con el mundo más simple posible. Esta es la fase que valida que el principio fundamental (World/Observer desacoplados) realmente funciona en código.

### 1.1 World mínimo
- `World` con estado simple: `temperature`, `light`, `object_position`, `hidden_variable` (booleano A/B para empezar, no continuo todavía).
- `world.step()` avanza el tiempo y aplica la regla causal de la hidden variable sobre `light`/`object_position`.
- `GroundTruth` separado, capturable en cada step.

**DoD:** `world.step()` corrido 1000 veces produce una traza de `GroundTruth` consistente y determinista dado un seed.

### 1.2 Sensor mínimo
- `PerfectSensor` y `NoisySensor(noise_std)`. Nada más todavía (sin delay, sin partial, sin probabilístico).
- `Observation` explícitamente **sin** `hidden_variable`.

**DoD:** test que confirma que `Observation` nunca contiene `hidden_variable`, ni siquiera indirectamente vía atributos ocultos.

### 1.3 Agent 0 — Reactive
- Sin memoria, sin modelo. Regla fija sobre la última observación.

**DoD:** corre 1000 steps sin error, produce una acción por step.

### 1.4 Agent 2 — Predictive (versión mínima)
- `WorldModel` mínimo: solo mantiene `P(hidden_state=A)` / `P(hidden_state=B)` como belief, actualizado con una regla bayesiana simple sobre lo observado.
- `predict(horizon=1)` — sin horizonte largo todavía.

**DoD:** después de 10.000 steps con `hidden_state` fijo, `P(hidden_state correcto)` converge visiblemente hacia 1 (aunque sea burdo).

### 1.5 Experiment Runner mínimo
- `Experiment(name, seed, steps, world, observer)`, `experiment.run()`.
- Persiste `config.json`, `ground_truth.json`, `observations.json`, `beliefs.json` (sin `report.html` todavía).
- Seed obligatorio y verificablemente determinista (correr dos veces con el mismo seed → mismo resultado, bit a bit).

**DoD:** `cognitive-observatory run experiment.yaml` corre el experimento de la variable oculta con Agent 0 y Agent 2, sin abrir navegador, y deja los JSON en `experiments/<fecha>_<nombre>_<seed>/`.

**🎯 Hito de Fase 1:** correr Agent 0 vs Agent 2 en el mismo mundo y poder decir, con un número, cuánto mejor predice Agent 2. Este es el primer resultado real del proyecto.

---

## Fase 2 — Métrica central + experimento de memoria

**Objetivo:** convertir el proyecto en algo que produce comparaciones, no solo una corrida aislada.

### 2.1 Prediction error como métrica formal
- `metrics/prediction.py` con `prediction_error(predicted_state, actual_state)`.
- Se registra por step en `metrics.json`, no solo al final.

**DoD:** `metrics.json` de una corrida muestra la curva de error bajando (o no) a lo largo del tiempo.

### 2.2 Agent 1 — Memory
- `WorkingMemory(capacity)` simple (buffer circular de últimas N observaciones).
- El belief se actualiza usando la memoria, no solo la última observación.

**DoD:** con `capacity=0` el comportamiento es idéntico a Agent 0; con `capacity` alta, converge más rápido que Agent 0 en el experimento de variable oculta.

### 2.3 Barrido de memoria (primer experimento comparativo real)
- Correr el mismo mundo/seed con `memory_capacity ∈ {0, 10, 50, 100, 500}`.
- Un script simple (no dashboard) que junta los `metrics.json` de las 5 corridas y produce una tabla o gráfica de accuracy final vs. capacity.

**DoD:** una gráfica/tabla que muestre si aparece o no el efecto de overfitting-por-memoria descrito en el spec (§8). El resultado puede confirmar o refutar la hipótesis — ambos casos son válidos, lo que importa es que el experimento corrió y produjo el dato.

**🎯 Hito de Fase 2:** el primer hallazgo real del proyecto, con gráfica, reproducible con seed fijo. A partir de acá el proyecto ya "existe" en el sentido de que produjo conocimiento, no solo código.

---

## Fase 3 — Reality-Model Divergence + Agent 3 (metacognición básica)

**Objetivo:** meter la pieza que conecta con la serie sobre la ilusión del yo.

### 3.1 Reality–Model Divergence como métrica
- `metrics/information.py` con una implementación concreta (empezar simple: distancia entre distribución de belief y el estado real, no algo information-theoretic sofisticado todavía).

### 3.2 Self Model mínimo
- `SelfModel` con `beliefs` y `confidence` por belief. Sin `capabilities`/`limitations` todavía — eso es Fase 5.
- `observer.evaluate_belief(belief_id)` devuelve confianza + evidencia (qué observaciones/memoria la sustentan).

### 3.3 Agent 3 — Metacognitive (versión mínima)
- Usa `SelfModel` para ajustar cuánto confía en su propio belief antes de actuar (ej. si confianza < umbral, explora en vez de explotar).

### 3.4 Calibración
- `metrics/behavior.py` — calibration check: cuando el agente dice "80% de confianza", ¿acierta ~80% de las veces? (bucketizar confidence vs. accuracy real).

**DoD:** correr Agent 0/1/2/3 en el mismo experimento y tabla comparativa de accuracy final + calibración. Gráfica de barras tipo la del spec original (§13).

**🎯 Hito de Fase 3:** los cuatro tipos de agente compitiendo en el mismo experimento, con métricas comparables. Este es el resultado más "mostrable" del proyecto hasta ahora.

---

## Fase 4 — Attention system

**Objetivo:** separar "información disponible" de "información procesada".

### 4.1 AttentionSystem base
- `UniformAttention` (equivalente a no tener atención — usar como baseline) y `SalienceAttention` (pondera por cuánto cambió el valor respecto al step anterior).

### 4.2 Experimento de atención
- Mismos datos exactos, dos observadores con distinta atención → comparar sus modelos internos resultantes (no solo accuracy final, sino *en qué difieren* los beliefs).

**DoD:** demostración concreta de que dos observadores con los mismos datos crudos terminan con modelos internos distintos solo por cómo atienden.

---

## Fase 5 — Self Model completo + reporting

**Objetivo:** cerrar el ciclo de metacognición y dejar de depender de scripts sueltos para ver resultados.

### 5.1 Self Model completo
- Agregar `capabilities`, `limitations` (ej. "hidden_state inaccessible" — que el propio agente lo reconozca explícitamente en su self-model, no solo que el diseñador lo sepa).

### 5.2 `report.html` por experimento
- Generación automática de un reporte legible por corrida (gráficas embebidas, no interactivo todavía — eso es el dashboard).

**DoD:** una corrida produce un `report.html` autocontenido que se puede abrir y entender sin tocar código ni notebooks.

---

## Fase 6 — Dashboard (opcional, evaluar si vale la pena)

**Objetivo:** instrumentación interactiva, solo si para este punto el engine ya demostró valor suficiente como para justificar la inversión.

### 6.1 API mínima
- FastAPI exponiendo experimentos corridos (lectura, no ejecución en vivo todavía).

### 6.2 Vista principal
- World vs. Observer lado a lado + prediction error en el tiempo.

### 6.3 Vista "Inside the observer"
- Beliefs actuales, memoria episódica reciente, predicciones con confianza, self-model.

**Nota:** esta fase es la más prescindible de todas. Si al llegar acá el valor ya está en los experimentos y reportes, el dashboard puede quedar como "nice to have" indefinidamente sin que el proyecto pierda su propósito.

---

## Fase 7 — Experiment Discovery (barridos masivos)

**Objetivo:** convertir el proyecto de "simulador de una arquitectura" a "buscador de arquitecturas".

### 7.1 Batch runner
- Definir grillas de configuración (`memory_capacity`, `sensor_noise`, `attention_strategy`, ...) y correr todas las combinaciones desatendido sobre la CLI existente (Fase 1.5 ya lo permite).

### 7.2 Análisis de barrido
- Script que identifica qué configuración minimiza reality-model divergence, y grafica interacciones entre parámetros (ej. memoria × sensores).

**DoD:** correr una noche entera de experimentos y despertar con una tabla de qué arquitectura ganó, y por qué (según las métricas, no intuición).

---

## Resumen visual del orden

```
Fase 0  Esqueleto repo
Fase 1  World + Sensor + Agent 0/2 + Experiment Runner   ← primer resultado real
Fase 2  Prediction error + Agent 1 + barrido de memoria   ← primer hallazgo
Fase 3  Divergence + Self Model mínimo + Agent 3          ← comparativa 4 agentes
Fase 4  Attention system
Fase 5  Self Model completo + report.html
Fase 6  Dashboard (evaluar si vale la pena antes de empezar)
Fase 7  Experiment Discovery / barridos masivos
```

Cada fase depende estrictamente de la anterior. No hay atajos hacia Fase 6 (dashboard) sin pasar por Fase 1 y 2 — es, literalmente, el orden en que el proyecto deja de ser una idea y empieza a producir datos.
