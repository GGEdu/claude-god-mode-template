---
paths:
  - "**/*.py"
---
# PyTorch — Reglas del stack

## Modelos
- Herencia de `nn.Module` — implementar `forward()` y `__init__()`
- `@torch.no_grad()` en inference — nunca olvidar
- `model.eval()` antes de inference, `model.train()` antes de training
- Inicialización explícita de pesos cuando el default no es adecuado

## Training
- Training loop explícito (no frameworks mágicos)
- `optimizer.zero_grad()` → `loss.backward()` → `optimizer.step()`
- Gradient clipping: `torch.nn.utils.clip_grad_norm_`
- Mixed precision: `torch.amp.autocast` + `GradScaler`
- Checkpoints periódicos: `torch.save(model.state_dict(), path)`

## Data
- `Dataset` + `DataLoader` con `num_workers > 0`
- `pin_memory=True` para transferencia GPU más rápida
- Transforms como pipeline: `Compose([...])` reproducible
- Validación split fija — nunca random por epoch

## Reproducibilidad
- Seeds al inicio: `torch.manual_seed()`, `np.random.seed()`, `random.seed()`
- `torch.use_deterministic_algorithms(True)` cuando sea posible
- Config files (YAML/Hydra) para hiperparámetros — no hardcoded

## Anti-patrones
- `.cuda()` hardcoded — usar `device = torch.device('cuda' if...)`
- Datos en GPU que no se necesitan — `.cpu()` para métricas
- Training sin validation — siempre monitorear overfitting
- Notebooks como producción — extraer a scripts reproducibles
