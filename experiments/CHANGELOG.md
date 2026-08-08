# Changelog de schema — experiments/

Este archivo documenta cambios de schema en los JSON persistidos por
`Experiment.save()`, para poder explicar por qué una corrida vieja no
calza byte a byte con una nueva del mismo seed.

## Fase 3 — cambio de schema en `beliefs.json` (commit que agrega Fase 3)

**Qué cambió:** el campo `confidence` en `beliefs.json`, para agentes sin
`world_model` (Agent 0 Reactive, Agent 1 Memory), pasó de `null` a `1.0`
(convención one-hot: un guess sin modelo probabilístico se trata como
"100% seguro" para poder calcular calibración de forma consistente entre
los 4 tipos de agente). Antes del refactor, esos agentes simplemente no
tenían un valor de confianza reportado.

**Qué NO cambió:** `metrics.json` (`prediction_error`) es **idéntico
byte a byte** en corridas regeneradas con el mismo seed/config — ya usaba
la misma distribución one-hot internamente desde Fase 2, el refactor solo
eliminó un cálculo duplicado. `ground_truth.json`, `observations.json` y
`config.json` tampoco cambian. Verificado regenerando las 6 corridas
afectadas (ver abajo) en un directorio aislado y comparando contra lo
commiteado.

**Archivo nuevo:** `divergence.json` (Reality-Model Divergence, spec §7.1)
no existe en corridas de Fase 1/Fase 2 — es una salida nueva de Fase 3,
no una diferencia de contenido de un archivo preexistente.

**Corridas generadas ANTES de este cambio** (su `beliefs.json` tiene
`confidence: null` donde hoy tendría `1.0`, y no tienen `divergence.json`):

- `2026-08-08_hidden_variable_42/` (agent_0_reactive)
- `2026-08-08_memory_sweep_capacity_0_42/`
- `2026-08-08_memory_sweep_capacity_10_42/`
- `2026-08-08_memory_sweep_capacity_50_42/`
- `2026-08-08_memory_sweep_capacity_100_42/`
- `2026-08-08_memory_sweep_capacity_500_42/`

Corridas generadas a partir de Fase 3 (incluida
`2026-08-08_four_agent_comparison_42/`) ya usan el schema nuevo.
