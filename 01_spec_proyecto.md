# Cognitive Observatory — Especificación del Proyecto

**Versión:** 1.0
**Estado:** Diseño previo a implementación
**Documento hermano:** `02_roadmap_fases.md` (orden de construcción)

---

## 1. Visión

> An open-source local laboratory for studying artificial observers, their internal models of reality, and the limits imposed by their cognitive architecture.

La palabra clave es **observer**, no *AI*. No estamos construyendo agentes inteligentes. Estamos construyendo agentes con acceso *parcial* a un mundo, e instrumentando qué representación interna construyen de él — y cuánto se aleja esa representación de lo que realmente está pasando.

### 1.1 La pregunta que el proyecto responde

No es una pregunta vaga tipo "¿puede un agente aprender?". Es una pregunta falsable, con número al final:

> Dada una arquitectura cognitiva X (memoria, atención, capacidad predictiva, modelo de sí mismo), ¿cuánto diverge el modelo interno del agente respecto al estado real del mundo, y cómo cambia esa divergencia al variar X?

Todo el diseño técnico existe para poder responder esa pregunta con un experimento reproducible, no para verse bien en una demo.

### 1.2 Qué NO es este proyecto

- No es una app de "agentes de IA" ni un producto.
- No usa LLMs en la v1. La arquitectura cognitiva se prueba primero con agentes matemáticos simples (reactivos, bayesianos, predictivos). Un `LLMObserver` es, en el mejor de los casos, una arquitectura más que se añade *después*, no el punto de partida.
- No es un framework general de agent-based modeling. Mesa (u otro framework similar) puede usarse más adelante como infraestructura de simulación en algún environment específico, pero el núcleo cognitivo (Observer, WorldModel, Memory, etc.) es propio y desacoplado — el objetivo es no terminar siendo "un wrapper de Mesa".
- No es, en su primera versión, un dashboard. El dashboard es instrumentación científica que se construye sobre un engine que ya funciona por línea de comandos, no al revés.

---

## 2. El principio fundamental

```
REAL WORLD
     │
     │ sensory channel (parcial, con ruido, con delay)
     ▼
  OBSERVER
     │
     │ inference
     ▼
INTERNAL MODEL
     │
     │ prediction
     ▼
  ACTION
     │
     └──────────────► WORLD
```

**Regla no negociable: el Observer nunca recibe el World directamente.**

El mundo puede contener una variable oculta:

```python
WorldState(
    temperature=23.7,
    light=0.82,
    object_position=(13, 7),
    object_velocity=(1, 0),
    hidden_variable=0.43,
)
```

Y el observador recibe solo lo que su sensor le permite:

```python
Observation(
    light=0.79,
    object_direction="east",
)
```

`hidden_variable` existe en el mundo. El observador no tiene acceso a ella — solo a sus efectos indirectos, si los hay. Esta separación es lo que hace posible medir algo real: qué puede inferir un observador sobre algo que nunca observa directamente.

Y, tan importante como lo anterior: **cada simulación conserva el Ground Truth completo** (estado real, variables, causalidad) por separado de lo que el observador cree. Esa diferencia — *lo que el agente cree* vs. *lo que realmente pasó* — es la métrica central de todo el proyecto (ver §7, Reality–Model Divergence).

---

## 3. Arquitectura general

```
                    ┌──────────────┐
                    │   Dashboard  │   (opcional, capa externa)
                    └──────┬───────┘
                           │
                     API / Events
                           │
                    ┌──────▼───────┐
                    │ Observatory  │
                    │    Engine    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           World        Observer     Metrics
```

**Decisión arquitectónica no negociable:** *the cognitive architecture must not depend on the UI.* El engine se puede invocar por línea de comandos (`cognitive-observatory run experiment.yaml`) sin levantar ningún navegador. Esto es lo que permite correr cientos de experimentos desatendidos y es, junto con la separación World/Observer, la decisión que más protege al proyecto de convertirse en "una app bonita sin experimento detrás".

### 3.1 Layout de carpetas (referencia completa — no todo se construye en v1)

```
cognitive-observatory/
├── core/
│   ├── world/
│   ├── observer/
│   ├── cognition/
│   ├── memory/
│   ├── actions/
│   └── experiments/
├── environments/
│   ├── gridworld/
│   ├── hidden_variable/
│   ├── causal_world/
│   └── temporal_world/
├── agents/
│   ├── reactive/
│   ├── predictive/
│   ├── bayesian/
│   └── active_inference/
├── metrics/
│   ├── information.py
│   ├── prediction.py
│   ├── complexity.py
│   └── behavior.py
├── experiments/
├── dashboard/
└── tests/
```

---

## 4. Subsistemas

### 4.1 World

Completamente independiente del observador.

```python
class World:
    state
    time

    def step(self):
        ...

    def get_state(self) -> GroundTruth:
        ...
```

```python
GroundTruth:
    timestamp
    variables
    entities
    causal_state
```

### 4.2 Sensors

El puente (con pérdida) entre World y Observer.

```python
class Sensor(ABC):
    def observe(self, world_state) -> Observation:
        ...
```

Variantes: `PerfectSensor`, `NoisySensor`, `LimitedRangeSensor`, `DelayedSensor`, `PartialSensor`, `ProbabilisticSensor`.

```python
sensor = NoisySensor(noise_std=0.2)
# REALITY: temperature = 23.73
# SENSOR:  temperature = 23.51
# El observador jamás sabe cuál era 23.73.
```

### 4.3 Attention

Información disponible ≠ información procesada. La atención decide qué parte de la observación realmente se usa.

```python
class AttentionSystem:
    def select(self, observation, internal_state) -> AttentionResult:
        ...
```

Variantes: `UniformAttention`, `RandomAttention`, `SalienceAttention`, `GoalDirectedAttention`, `PredictiveAttention`.

Esto habilita experimentos tipo: dos observadores reciben exactamente los mismos datos, pero con distinta atención, y se comparan sus modelos internos resultantes.

### 4.4 Memory

No una sola clase `Memory` — cuatro subsistemas separados (aunque las primeras implementaciones pueden ser simples):

- **Working Memory** — capacidad limitada (`WorkingMemory(capacity=7)`).
- **Episodic Memory** — `Episode(timestamp, observation, action, outcome)`.
- **Semantic Memory** — representaciones abstractas tipo "when X happens, Y usually follows".
- **Procedural Memory** — cómo hacer cosas, no qué pasó.

Permite experimentar directamente con límites de memoria (ver §8, hallazgo esperado de overfitting con memoria excesiva).

### 4.5 Internal World Model

El corazón conceptual del proyecto.

```python
class WorldModel:
    beliefs
    entities
    causal_relations
    predictions
    uncertainty
```

Ejemplo: el mundo tiene A → B → C. El observador solo ve "A ocurrió" y "C ocurrió", e infiere "A probablemente causa C" — inferencia que puede estar equivocada, y esa equivocación es exactamente lo que se mide.

### 4.6 Prediction Engine

```python
prediction = observer.predict(horizon=5)
# t+1 → object east
# t+2 → object east
# t+3 → object north
```

Produce la métrica central de precisión predictiva:

```python
prediction_error = distance(predicted_state, actual_state)
```

Debe ser un sistema extensible, no una sola métrica fija.

### 4.7 Self Model (metacognición)

Este es el subsistema que conecta directamente con la serie sobre la ilusión del yo.

```python
SelfModel:
    position
    capabilities
    limitations
    memories
    goals
    beliefs
    uncertainty
```

Permite el salto de "creo que el objeto está al norte" a "creo que creo que el objeto está al norte":

```python
observer.evaluate_belief(belief_id)
# belief: object_is_north
# confidence: 0.73
# evidence: [sensor_12, memory_384, prediction_92]
```

### 4.8 Action / ciclo completo

```
OBSERVE → ATTEND → UPDATE MEMORY → UPDATE WORLD MODEL
   → PREDICT → EVALUATE → SELECT ACTION → WORLD
```

Este ciclo se ejecuta en cada timestep.

---

## 5. Tipos de agente

Cuatro arquitecturas iniciales, ordenadas como escalera de complejidad (cada una es baseline de la siguiente):

| Agente | Ciclo | Qué mide |
|---|---|---|
| **Agent 0 — Reactive** | observation → rule → action | Baseline sin memoria |
| **Agent 1 — Memory** | observation → memory → action | Cuánto aporta recordar |
| **Agent 2 — Predictive** | observation → world model → prediction → action | Cuánto aporta anticipar |
| **Agent 3 — Metacognitive** | observation → world model → belief → confidence → self-model → action | Si "saber que no sabe" mejora el desempeño |

Más adelante, opcional: **Agent 4 — Active Inference** (percepción y acción como un único circuito cerrado con incertidumbre, en vez de módulos independientes).

---

## 6. El experimento fundacional: Hidden Variable

El mundo tiene `temperature`, `light`, `object_position`, y una `hidden_variable` **nunca observable directamente**, que controla efectos indirectos:

```
hidden_state = A  →  light tends to increase, object moves north
hidden_state = B  →  light tends to decrease, object moves south
```

El agente empieza sin conocer esta relación. Tras N pasos, se compara:

```
Ground Truth:  Hidden state = B
Agent Model:   P(A) = 0.12, P(B) = 0.88
```

Este es el primer experimento que el proyecto debe poder correr de punta a punta — antes que cualquier otra cosa (dashboard, self-model, atención avanzada).

---

## 7. Métricas

Cada experimento registra, como mínimo:

- **Accuracy** — qué tan correcto es el modelo.
- **Prediction error** — qué tan malas son las predicciones.
- **Information loss** — cuánta información del mundo nunca llega al agente.
- **Model complexity** — cuán complejo es el modelo interno.
- **Memory utilization** — cuánto usa de su memoria disponible.
- **Adaptation rate** — qué tan rápido actualiza creencias.
- **Calibration** — si dice 80% de confianza, ¿acierta ~80% de las veces?

### 7.1 Reality–Model Divergence

La métrica que probablemente se convierta en el indicador central del Observatory:

```
Reality complexity → Observer bandwidth → Information bottleneck
    → Internal model → Model divergence
```

Es la conexión directa con la idea de "realidad comprimida": cuánto se pierde, estructuralmente, al pasar por un observador con ancho de banda limitado.

---

## 8. Hallazgos esperados (hipótesis, no garantías)

El diseño está pensado para poder producir sorpresas medibles, por ejemplo:

- Memoria: rendimiento mejora con más memoria, hasta un punto — después, overfitting y el rendimiento empeora.
- Sensores: más sensores → más información, pero también más carga cognitiva → peores decisiones si la atención no escala igual.

Si el proyecto nunca produce un resultado que contradiga la intuición inicial, probablemente significa que el experimento fue demasiado simple o que no se corrió con suficiente variación — no que "no hay nada que encontrar".

---

## 9. Experiment Runner (reproducibilidad)

```python
experiment = Experiment(
    name="hidden_variable",
    seed=42,
    steps=10000,
    world=HiddenVariableWorld(...),
    observer=PredictiveObserver(memory_capacity=100),
)
result = experiment.run()
```

La semilla es **obligatoria**. `seed=42` debe producir exactamente el mismo experimento siempre.

Cada corrida se persiste así:

```
experiments/
    2026-08-08_hidden_variable_42/
        config.json
        ground_truth.json
        observations.json
        beliefs.json
        predictions.json
        metrics.json
        report.html
```

---

## 10. Dashboard (visión a futuro, no v1)

Instrumentación científica, no producto. Dos vistas centrales:

1. **Vista principal** — World vs. Observer lado a lado, prediction error en el tiempo, reality/model divergence.
2. **"Inside the observer"** — abrir el agente y ver sus creencias actuales, memoria episódica reciente, predicciones con confianza, y su self-model (capacidades y limitaciones que él mismo reconoce).

---

## 11. Experiment Discovery (visión a futuro, no v1)

Una vez que el loop básico funciona, se puede automatizar barridos de configuración:

```
Run N variaciones de:
    memory_capacity, sensor_noise, attention_strategy,
    prediction_horizon, self_model
→ ¿qué configuración minimiza reality-model divergence?
```

Esto convierte el proyecto en un buscador de arquitecturas cognitivas, no solo un simulador de una arquitectura fija.

---

## 12. Stack técnico

```
Python 3.12+
NumPy, SciPy, Pandas
Pydantic
SQLite
FastAPI          (solo cuando exista dashboard)
React + TypeScript  (solo cuando exista dashboard)
Recharts / Canvas / SVG (solo cuando exista dashboard)

pytest, ruff, mypy
```

Mesa puede evaluarse más adelante como infraestructura de simulación para un `environment` específico — **no como dependencia de v1**, para no acoplar el core cognitivo a un framework externo desde el principio.

---

## 13. Alcance explícito de la v1 (qué queda fuera al empezar)

Este documento describe el proyecto completo como visión de largo plazo. La v1 real — lo que efectivamente se construye primero — es deliberadamente mucho más chica. Ver `02_roadmap_fases.md` para el desglose, pero como regla general quedan **fuera de la v1**:

- Dashboard / UI
- Self Model y metacognición
- Attention system (más allá de "uniform")
- Semantic y Procedural Memory
- Mesa u otro framework de simulación externo
- LLMObserver
- Active Inference agent
- Experiment Discovery / barridos masivos

La v1 existe únicamente para probar, de punta a punta con datos reales, que el principio fundamental (§2) produce algo medible con el experimento de la variable oculta (§6).
