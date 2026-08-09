# Cognitive Observatory - Dashboard (Fase 6)

Frontend de solo lectura sobre las corridas persistidas en `experiments/`,
vía la API de `dashboard/api/` (Fase 6.1).

## Desarrollo

Con el backend corriendo (desde la raíz del repo):

```
.venv\Scripts\python -m uvicorn dashboard.api.main:app
```

Y en otra terminal, el frontend:

```
npm install
npm run dev
```

Abre `http://localhost:5173`. El dev server proxea `/api/*` hacia
`http://127.0.0.1:8000` (ver `vite.config.ts`) - si corrés el backend en
otro puerto, ajustá el `target` ahí.

## Build

```
npm run build
```

Type-checkea con `tsc` y genera `dist/` con Vite (no se commitea).
