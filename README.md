# Cognitive Observatory

Laboratorio local para estudiar observadores artificiales, sus modelos internos
del mundo, y los límites que impone su arquitectura cognitiva.

Ver `01_spec_proyecto.md` (especificación) y `02_roadmap_fases.md` (orden de
construcción) — son la fuente de verdad del proyecto.

## Desarrollo

```
py -3.12 -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
.venv\Scripts\pytest
.venv\Scripts\ruff check .
.venv\Scripts\mypy .
```

Estado actual: Fase 0 (esqueleto del repo).
