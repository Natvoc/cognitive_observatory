# Cognitive Observatory

> An open-source local laboratory for studying artificial observers, their
> internal models of reality, and the limits imposed by their cognitive
> architecture.

Laboratorio personal — no un framework, no un producto. La palabra clave es
**observer**, no *AI*: la idea no es construir agentes inteligentes, sino
agentes con acceso *parcial* a un mundo, e instrumentar qué representación
interna construyen de él y cuánto se aleja esa representación de lo que
realmente está pasando.

La pregunta que responde el proyecto tiene número al final: dada una
arquitectura cognitiva X (memoria, atención, capacidad predictiva, modelo de
sí mismo), ¿cuánto diverge el modelo interno del agente respecto al estado
real del mundo, y cómo cambia esa divergencia al variar X?

## El principio fundamental

```
REAL WORLD → (sensor, con pérdida) → OBSERVER → INTERNAL MODEL → ACTION → WORLD
```

**El Observer nunca recibe el World directamente.** El mundo tiene estado
completo (`GroundTruth`); el observador solo recibe lo que su sensor le deja
pasar (`Observation`), que puede tener ruido, ser parcial, o directamente
omitir variables que existen en el mundo. Esa diferencia — lo que el agente
cree vs. lo que realmente pasó — es la métrica central de todo el proyecto.

El primer experimento (y el que valida este principio de punta a punta) es
**hidden_variable**: el mundo tiene una variable oculta (`A` o `B`) que nunca
se observa directamente, pero que influye indirectamente en variables sí
observables (`light`, `object_position`). El agente tiene que inferir cuál es
el estado oculto a partir de esos efectos indirectos — nunca lo ve.

## Qué NO es este proyecto

- No es una app de "agentes de IA" ni un producto.
- No usa LLMs en la v1 — la arquitectura cognitiva se prueba primero con
  agentes matemáticos simples (reactivos, con memoria, bayesianos). Un
  `LLMObserver` sería, en el mejor de los casos, una arquitectura más que se
  agrega después.
- No es un framework general de agent-based modeling. El núcleo cognitivo
  (Observer, WorldModel, Memory, etc.) es propio y desacoplado, para no
  terminar siendo un wrapper de otra librería.
- El dashboard (Fase 6) es de solo lectura sobre corridas ya persistidas —
  no ejecuta experimentos en vivo ni escribe nada. Correr experimentos
  sigue siendo trabajo de la CLI/scripts; el dashboard es instrumentación
  construida sobre un engine que ya funcionaba, no al revés.

## Estado actual

**Fase 0 — Esqueleto del repo.** Estructura instalable, testeable, CLI
mínimo (`cognitive-observatory --version`).

**Fase 1 — Loop mínimo.** `World` + `Sensor` + Agent 0 (reactivo, sin
memoria) vs. Agent 2 (predictivo, con belief bayesiano) corriendo de punta a
punta sobre el experimento de variable oculta, con Experiment Runner
determinista (mismo seed → mismo resultado, bit a bit). Resultado: en una
corrida de 10.000 steps (bajo ruido de sensor moderado), Agent 2 alcanza
accuracy 0.9997 vs. 0.9845 de Agent 0, y queda perfectamente estable una vez
que converge (Agent 0 sigue cometiendo errores ocasionales por reaccionar a
una sola observación ruidosa cada vez).

**Fase 2 — Métrica de error + memoria.** `prediction_error` (Brier score)
registrado por step. Agent 1 (con memoria de capacidad fija) se agrega a la
comparación. Barrido de `memory_capacity ∈ {0, 10, 50, 100, 500}` sobre el
mismo mundo/seed: pasar de capacity=0 a 10 sube la accuracy de 0.895 a 1.000
(bajo ruido de sensor alto). No aparece el efecto de "overfitting por
memoria excesiva" hipotetizado — resultado esperable en un mundo
*estacionario* (el hidden_state no cambia durante la corrida), donde
promediar una señal ruidosa con más muestras solo puede ayudar o estancarse,
nunca empeorar. Ese tipo de resultado — confirmar o refutar una hipótesis
con un número reproducible — es lo que este proyecto busca producir.

**Fase 3 — Reality-Model Divergence + Self Model + Agent 3.**
`reality_model_divergence` (distancia simple, no information-theoretic
todavía) registrada por step. `SelfModel.evaluate_belief()` (confianza +
evidencia). Agent 3 explota su belief si su confianza supera un umbral, y
explora (muestrea proporcional al belief) si no. Con los 4 agentes
compitiendo en el mismo experimento, el hallazgo de calibración: Agent 0 y
Agent 1 reportan 100% de confianza siempre pero aciertan 88.8%/99.4% de las
veces (sobreconfiados por construcción, no representan incertidumbre real);
Agent 2 y Agent 3 reportan una confianza que sí coincide con su accuracy
real (~100%/~100%).

**Fase 4 — Attention system.** `UniformAttention` (baseline) y
`SalienceAttention` (pondera por cuánto cambió `light` desde el step
anterior). Dos observadores Predictive reciben exactamente las mismas
observaciones crudas y terminan con beliefs distintos solo por cómo
atienden (diferencia máxima de belief de 0.74 en un mismo step, 4/10000
guesses en desacuerdo).

**Fase 5 — Self Model completo + reporting.** `SelfModel` gana
`capabilities`/`limitations` (metadata declarada por diseño, no
autoconocimiento emergente — Agent 3 se auto-declara "hidden_state
inaccessible"). Cada corrida vía CLI genera automáticamente un
`report.html` autocontenido (sin JS, sin recursos externos) con
accuracy/prediction_error/divergence por agente.

**Fase 6 — Dashboard** (evaluamos que valía la pena antes de empezar).
6.1: API de FastAPI de solo lectura sobre `experiments/` (`GET /runs`,
`GET /runs/{run_id}`), sin ningún endpoint que ejecute o escriba nada.
6.2: frontend (Vite + React + TypeScript + Recharts) con selector de
corridas y vista principal — World (ground truth) y Observer (belief)
lado a lado evolucionando en el tiempo, más `prediction_error` por
agente. 6.3: vista "Inside the observer" — beliefs actuales con
confianza, self-model (capabilities/limitations) para agentes
metacognitivos, e historial reciente reconstruido de los datos ya
persistidos (explícitamente **no** el subsistema formal de Episodic
Memory, que no está implementado). Ver `dashboard/web/README.md` para
correrlo.

**Fase 7 — Experiment Discovery.** De "simulador de una arquitectura" a
"buscador de arquitecturas": un barrido desatendido de 7 arquitecturas ×
3 niveles de ruido de sensor (`scripts/batch_runner.py`), analizado por
`scripts/analyze_batch.py` (tabla + heatmap SVG de qué arquitectura
minimiza `reality_model_divergence`, y por qué). El hallazgo: el agente
con memoria simple (`capacity=200`) le gana en velocidad de convergencia
a los agentes bayesianos (Predictive/Metacognitive) en los tres niveles
de ruido — el modelo de likelihood fijo que usan estos últimos resultó
ser una aproximación más cruda del proceso real que un promedio
adaptativo. No confirma la intuición de que "más sofisticado es mejor".

Con esto queda completo el roadmap de `02_roadmap_fases.md` (Fase 0 a
Fase 7).

Cada corrida queda persistida en `experiments/<fecha>_<nombre>_<seed>/` con
`config.json`, `ground_truth.json`, `observations.json`, `beliefs.json`,
`metrics.json` y `divergence.json` (desde Fase 3 — ver
`experiments/CHANGELOG.md` para el detalle de ese cambio de schema).

## Cómo correr un experimento

```
cognitive-observatory run experiment.yaml
```

## Desarrollo

**Windows:**
```
py -3.12 -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
.venv\Scripts\pytest
.venv\Scripts\ruff check .
.venv\Scripts\mypy .
```

**macOS / Linux:**
```
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/mypy .
```

## Stack técnico

Python 3.12+, pytest/ruff/mypy, PyYAML. Desde Fase 6 (dashboard):
FastAPI/pydantic/uvicorn (API de solo lectura) y, en `dashboard/web/`,
Vite + React + TypeScript + Recharts. Sin nada de esto hasta que la fase
correspondiente lo necesitó de verdad.
