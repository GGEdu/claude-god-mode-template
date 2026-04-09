# Python API Conventions

Aplica siempre estas convenciones al trabajar en APIs Python.

## Type Hints (OBLIGATORIO en todo código nuevo)

```python
# CORRECTO: type hints en funciones y métodos
def get_user(user_id: int) -> User | None:
    ...

def create_order(data: OrderCreateSchema) -> Order:
    ...

# INCORRECTO: sin type hints
def get_user(user_id):
    ...
```

## Estructura de proyecto Django REST Framework

```
proyecto/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   └── mi_app/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py           ← ViewSets delgados
│       ├── services.py        ← Lógica de negocio
│       ├── urls.py
│       ├── permissions.py
│       └── tests/
│           ├── test_models.py
│           ├── test_views.py
│           └── test_services.py
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

## ViewSets delgados — lógica en Services

```python
# CORRECTO: ViewSet delgado, delega en service
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.create(serializer.validated_data, user=request.user)
        return Response(OrderSerializer(order).data, status=201)

# INCORRECTO: lógica de negocio en el ViewSet
class OrderViewSet(viewsets.ModelViewSet):
    def create(self, request):
        # 50 líneas de lógica de negocio aquí...
```

## Serializers con validación

```python
class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['product_id', 'quantity', 'notes']

    def validate_quantity(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser positiva.")
        return value
```

## Services pattern

```python
# services.py
class OrderService:
    @staticmethod
    def create(data: dict, user: User) -> Order:
        """Crea un pedido validando stock disponible."""
        product = get_object_or_404(Product, id=data['product_id'])
        if product.stock < data['quantity']:
            raise ValidationError("Stock insuficiente.")
        return Order.objects.create(**data, created_by=user)
```

## Consultas ORM — evitar N+1

```python
# CORRECTO: select_related para FK, prefetch_related para M2M
orders = Order.objects.select_related('user', 'product').prefetch_related('items').all()

# INCORRECTO: N+1 queries
orders = Order.objects.all()
for order in orders:
    print(order.user.email)  # ← query adicional por cada order
```

## FastAPI (alternativa)

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/orders/", response_model=OrderResponse, status_code=201)
async def create_order(
    data: OrderCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    return await OrderService.create(db, data, current_user)
```

## Tests con pytest

```python
import pytest
from django.test import TestCase

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def order(db, user):
    return OrderFactory(created_by=user)

def test_create_order_insufficient_stock(db, user):
    product = ProductFactory(stock=0)
    with pytest.raises(ValidationError, match="Stock insuficiente"):
        OrderService.create({'product_id': product.id, 'quantity': 1}, user)
```

## Linting con Ruff

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM"]
ignore = ["E501"]
```

## Anti-patrones a evitar

- **NO** usar `except Exception: pass` — manejar errores explícitamente
- **NO** queries crudas con string interpolation (SQL injection)
- **NO** lógica de negocio en serializers ni vistas
- **NO** variables mutables como valores por defecto en funciones (`def f(lista=[]):`)
- **NO** importar `*` de módulos
