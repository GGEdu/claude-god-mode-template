# [NOMBRE DEL PROYECTO]

## Stack
- **Framework ML**: PyTorch 2+
- **Lenguaje**: Python 3.12+
- **GPU**: CUDA 12+ / MPS (Apple Silicon)
- **Tests**: pytest
- **Linter**: Ruff

## Arquitectura
[DESCRIPCIÓN: modelo de clasificación, generativo, RL, etc.]

## Convenciones
- Commits: Conventional Commits
- Reproducibilidad: seeds fijos, configs versionadas
- Type hints obligatorios (mypy strict mode)
- Experimentos tracked con wandb o mlflow

## Comandos críticos
- `/plan` — Antes de implementar cualquier feature
- `/tdd` — Ciclo RED-GREEN-REFACTOR
- `/benchmark` — Medir performance de modelo

## Estructura del proyecto
```
src/
├── data/                ← Datasets, dataloaders, transforms
├── models/              ← Arquitecturas (nn.Module)
├── training/            ← Training loops, optimizers
├── evaluation/          ← Métricas, inference
├── config/              ← Hydra/YAML configs
└── utils/               ← Logging, reproducibility
notebooks/               ← Exploración (no producción)
scripts/                 ← Entry points (train, eval, export)
tests/                   ← pytest
```

## Variables de entorno necesarias
- `CUDA_VISIBLE_DEVICES` — GPUs disponibles
- `WANDB_API_KEY` — Tracking de experimentos
- `DATA_DIR` — Directorio de datasets

## Notas del proyecto
[AGREGAR: modelo base, dataset, métricas target, etc.]
