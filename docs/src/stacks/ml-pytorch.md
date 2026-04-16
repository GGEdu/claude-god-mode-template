# Stack: ML PyTorch

**Versiones:** Python 3.12 · PyTorch 2.4 · CUDA 12 · Ruff · pytest · wandb

## Inicializar

```bash
make dev-stack STACK=ml-pytorch
```

Activa: reglas PyTorch, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow-runner <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/benchmark` | Medir regresiones de rendimiento en training/inference |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Las prácticas `pytorch-patterns`, `tensor-operations`, `training-loops`, `distributed-training` y `model-evaluation` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Data / Model / Training

```text
src/
├── models/                  ← Definición de módulos
│   ├── __init__.py
│   ├── transformer.py       ← Arquitecturas (heredar de nn.Module)
│   └── attention.py         ← Componentes reutilizables
├── data/                    ← Data loading y preprocessing
│   ├── __init__.py
│   ├── datasets.py          ← Clases Dataset personalizado
│   └── loaders.py           ← DataLoader factories
├── training/                ← Training loops y optimización
│   ├── __init__.py
│   ├── trainer.py           ← Clase Trainer (epoch loop)
│   ├── loss.py              ← Loss functions personalizados
│   └── metrics.py           ← Validación y evaluación
├── utils/                   ← Helpers
│   ├── __init__.py
│   ├── config.py            ← Configuración centralizada
│   └── device.py            ← Abstracción CPU/GPU/multi-GPU
└── inference/               ← Predicción en producción
    ├── __init__.py
    └── pipeline.py          ← Clase para servir el modelo
tests/
├── test_models.py
├── test_data.py
└── test_training.py
```

### Módulos — Heredar de nn.Module

```python
# CORRECTO: subclase de nn.Module con forward
import torch
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# INCORRECTO: lógica de tensor suelta sin nn.Module
def bad_forward(x, w1, w2):
    x = torch.matmul(x, w1)
    x = torch.relu(x)
    return torch.matmul(x, w2)
```

### DataLoader — Batch eficiente

```python
# CORRECTO: Dataset personalizado + DataLoader
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, features: list, labels: list):
        self.features = features
        self.labels = labels
    
    def __len__(self) -> int:
        return len(self.features)
    
    def __getitem__(self, idx: int) -> tuple:
        return torch.tensor(self.features[idx], dtype=torch.float32), \
               torch.tensor(self.labels[idx], dtype=torch.long)

# DataLoader con batching automático
train_loader = DataLoader(
    CustomDataset(features, labels),
    batch_size=32,
    shuffle=True,
    num_workers=4,  # ← Paralelización
    pin_memory=True  # ← Si usas GPU
)

# INCORRECTO: procesar muestras de una en una
for feature, label in features, labels:
    output = model(feature.unsqueeze(0))
```

### Training Loop — Estructura estándar

```python
# CORRECTO: loop de entrenamiento con validación
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SimpleNet(10, 64, 2).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

for epoch in range(num_epochs):
    # Training
    model.train()
    train_loss = 0.0
    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
    
    # Validation
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for X_val, y_val in val_loader:
            X_val, y_val = X_val.to(device), y_val.to(device)
            outputs = model(X_val)
            loss = criterion(outputs, y_val)
            val_loss += loss.item()
    
    print(f"Epoch {epoch+1}: train_loss={train_loss/len(train_loader):.4f}, "
          f"val_loss={val_loss/len(val_loader):.4f}")

# INCORRECTO: sin model.eval() en validación (dropout activado)
model.eval()  # ← OBLIGATORIO antes de validar
with torch.no_grad():
    for X, y in val_loader:
        outputs = model(X)
```

### Checkpointing — Guardar y restaurar

```python
# CORRECTO: guardar estado completo
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}
torch.save(checkpoint, 'model_checkpoint.pt')

# Cargar
checkpoint = torch.load('model_checkpoint.pt')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
epoch = checkpoint['epoch']

# INCORRECTO: guardar solo el modelo sin optimizer
torch.save(model.state_dict(), 'bad_model.pt')  # ← No puedes continuar training
```

### Distributed Training — multi-GPU

```python
# CORRECTO: DistributedDataParallel para multi-GPU
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

# Inicializar proceso distribuido
torch.distributed.init_process_group(backend='nccl')
model = SimpleNet(10, 64, 2)
model = model.to(rank)
model = DDP(model, device_ids=[rank])

# DistributedSampler para no duplicar datos
sampler = DistributedSampler(dataset, shuffle=True)
loader = DataLoader(dataset, batch_size=32, sampler=sampler)

# INCORRECTO: DataParallel (más lento que DDP)
model = nn.DataParallel(model)  # ← Solo para single-machine multi-GPU
```

### Testing — pytest con fixtures

```python
# tests/test_models.py
import pytest
import torch
from src.models.transformer import SimpleNet

@pytest.fixture
def model():
    return SimpleNet(input_dim=10, hidden_dim=64, output_dim=2)

@pytest.fixture
def sample_input():
    return torch.randn(4, 10)  # batch_size=4, input_dim=10

def test_model_output_shape(model, sample_input):
    output = model(sample_input)
    assert output.shape == (4, 2)

def test_model_to_device(model):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    assert next(model.parameters()).device.type == device.type

def test_forward_backward(model, sample_input):
    optimizer = torch.optim.Adam(model.parameters())
    loss_fn = torch.nn.MSELoss()
    
    target = torch.randn(4, 2)
    output = model(sample_input)
    loss = loss_fn(output, target)
    
    loss.backward()
    optimizer.step()
    
    assert loss.item() > 0
```

---

## Anti-patrones a evitar

- **Modelo sin herencia de nn.Module** — siempre usar clases que hereden de nn.Module
- **Sin model.eval() en validación** — causará resultados incorrectos con dropout/batch norm
- **Tensores en CPU y GPU mezclados** — asegurar que todo esté en el mismo device
- **DataLoader sin num_workers** — carga lenta sin paralelización
- **Sin gradient clipping en LSTM/GRU** — causará exploding gradients
- **Guardar solo model.state_dict()** — perder optimizer state imposibilita continuar training
- **Sin scheduler de learning rate** — convergencia lenta o inestable
- **Concatenar tensores en loop** — usar listas y stacking al final
- **Sin validación separada del training** — overfitting no detectado

---

## Comandos útiles

```bash
# Desarrollo
python -m src.training.trainer --config config.yaml

# Tests
pytest tests/ -v --cov=src

# Linting
ruff check src/ tests/
ruff format src/ tests/

# Training con W&B
python -m src.training.trainer --config config.yaml --wandb

# Inference
python -m src.inference.pipeline --model model_checkpoint.pt --input data.csv

# GPU diagnostics
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

## Variables de entorno

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3    # GPUs a usar
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
PYTHONPATH=.

WANDB_PROJECT=ml-project
WANDB_ENTITY=your-team

BATCH_SIZE=32
LEARNING_RATE=0.001
EPOCHS=100
SEED=42
```

---

## Ejemplo completo

→ [CLAUDE.md para PyTorch Training](/examples/pytorch-training-CLAUDE)
