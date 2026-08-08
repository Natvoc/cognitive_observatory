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
- No es, en esta etapa, un dashboard. Lo que existe hoy corre por línea de
  comandos; el dashboard es instrumentación que se construiría sobre un
  engine que ya funciona, no al revés.

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

Cada corrida queda persistida en `experiments/<fecha>_<nombre>_<seed>/` con
`config.json`, `ground_truth.json`, `observations.json`, `beliefs.json` y
`metrics.json`.

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

Python 3.12+, pytest/ruff/mypy, PyYAML — sin dependencias de ML ni web hasta
que una fase futura las necesite de verdad.
