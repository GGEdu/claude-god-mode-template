# Stack: Python API

**Versiones:** Python 3.12+ · Django REST Framework o FastAPI · PostgreSQL · pytest

## Inicializar

```bash
make dev-stack STACK=python-api
```

Activa: reglas Python API, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/benchmark` | Medir regresiones de rendimiento |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Además de los comandos anteriores, este stack incluye comandos universales (`/ck`, `/plankton-code-quality`, `/context-budget`, etc.).

Las prácticas `python-patterns`, `django-tdd`, `django-security`, `api-design`, `database-migrations` y `postgres-patterns` se aplican como skills embebidas en agentes.

---

## Convenciones clave

### Type hints obligatorios (Python 3.12)

```python
# Sin imports de typing para los tipos básicos
def get_users(active: bool = True) -> list[dict]: ...
def find_user(ref: str) -> 'User | None': ...
```

### Django REST Framework

```python
# ViewSet delgado — lógica en Service
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductService.get_queryset(self.request.user)

    def perform_create(self, serializer):
        ProductService.create(serializer.validated_data, self.request.user)
```

### Prevención de N+1

```python
# CORRECTO: eager loading explícito
queryset = Order.objects.select_related('user').prefetch_related('items__product')

# CORRECTO: scope reutilizable
class OrderManager(models.Manager):
    def with_details(self):
        return self.select_related('user').prefetch_related('items')
```

### Tests con pytest

```python
# conftest.py con fixtures
@pytest.fixture
def api_client(db):
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user_factory):
    user = user_factory()
    api_client.force_authenticate(user=user)
    return api_client, user
```

---

## Anti-patrones a evitar

- Fat views (lógica de negocio en ViewSets) — lógica en `services/`
- `Model.objects.all()` sin filtros en endpoints paginados
- Serializers anidados sin `depth` controlado
- `settings.py` sin separación dev/prod/test
- Queries dentro de bucles — siempre `select_related` / `prefetch_related`

---

## Comandos útiles (Django)

```bash
# Arrancar servidor
python manage.py runserver

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Tests con pytest
pytest
pytest tests/api/ -v
pytest --cov=apps --cov-report=html

# Shell con contexto
python manage.py shell_plus  # necesita django-extensions
```

## FastAPI (alternativa)

```python
@router.get("/products", response_model=list[ProductSchema])
async def list_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProductService.list(db, user_id=current_user.id)
```

---

## Ejemplo completo

→ [CLAUDE.md para Django REST API](/examples/django-api-CLAUDE)
