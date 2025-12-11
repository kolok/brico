# Tests - Webapp Agent Notes (Django + Hotwire)

This document describes the conventions and practices for testing in the webapp application.

## Overview

- **Testing framework**: pytest with pytest-django
- **Data fixtures**: factory-boy (FactoryBoy)
- **Main command**: `make test` or `uv run pytest`
- **Minimum coverage**: ≥ 80% for backend

## Test Structure

### File Organization

Each Django app has its own `tests/` folder that follows the same structure as the app itself.

**Example structure:**

```
audits/
├── models/
│   └── audit.py          # Source code
├── views/
│   └── audits.py         # Source code
└── tests/
    ├── factories.py      # Factories for fixtures
    ├── models/
    │   └── test_audit.py  # Model tests
    └── views/
        └── test_audits.py # View tests
```

**Mapping rule:**

- `audits/models/audit.py` → `audits/tests/models/test_audit.py`
- `audits/views/audits.py` → `audits/tests/views/test_audits.py`
- `audits/forms.py` → `audits/tests/test_forms.py`

### Naming Conventions

#### Test Files

- `test_` prefix for all test files
- File name corresponds to the tested module with the `test_` prefix
- Examples: `test_audit.py`, `test_forms.py`, `test_views.py`

#### Test Classes

Each public class (model, form, function) has its corresponding test class.

**Source code example:**

```python
# audits/models/audit.py
class AuditLibrary(models.Model):
    pass

class MyForm(forms.Form):
    pass

def my_function():
    pass
```

**Corresponding test classes:**

```python
# audits/tests/models/test_audit.py
@pytest.mark.django_db
class TestAuditLibrary:
    def test_something(self):
        pass

# audits/tests/test_forms.py
@pytest.mark.django_db
class TestMyForm:
    def test_something(self):
        pass

# audits/tests/test_my_function.py (or in the appropriate module)
class TestMyFunction:
    def test_something(self):
        pass
```

#### Test Methods

- `test_` prefix for all test methods
- Descriptive names: `test_slug_generation_automatic`, `test_organization_foreign_key`
- Use `assert` for assertions (not `self.assert*`)

### Test Scope

- ✅ **Tested**: all public functions and classes
- ❌ **Not tested**: private functions (prefixed with `_`)

## Running Tests

### Main Commands

```bash
# All tests
make test

# With uv directly
uv run pytest

# Tests for a specific app
uv run pytest audits/tests/

# Tests for a specific file
uv run pytest audits/tests/models/test_audit.py

# Tests for a specific class
uv run pytest audits/tests/models/test_audit.py::TestAuditLibrary

# Tests for a specific method
uv run pytest audits/tests/models/test_audit.py::TestAuditLibrary::test_slug_generation_automatic

# Verbose mode
uv run pytest -v

# Stop at first failure
uv run pytest -x

# Show print statements
uv run pytest -s
```

## Factory Boy (Data Fixtures)

### Usage

Factory Boy is used to create Django model instances in tests.

**Factory location:**

- Each app has its `tests/factories.py` file
- Factories are organized by model

**Factory example:**

```python
# audits/tests/factories.py
import factory
from audits.models.audit import AuditLibrary
from factory.faker import Faker
from organization.tests.factories import OrganizationFactory

class AuditLibraryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuditLibrary

    name = Faker("catch_phrase")
    organization = factory.SubFactory(OrganizationFactory)
```

**Usage in tests:**

```python
@pytest.mark.django_db
class TestAuditLibrary:
    def test_something(self):
        library = AuditLibraryFactory(name="My Library")
        assert library.name == "My Library"
```

### Pytest Fixtures

Fixtures can be defined at the module or test file level:

```python
@pytest.fixture
def organization():
    return OrganizationFactory()

@pytest.mark.django_db
class TestAuditLibrary:
    def test_something(self, organization):
        library = AuditLibraryFactory(organization=organization)
        assert library.organization == organization
```

## Best Practices

### 1. Using `@pytest.mark.django_db`

Always use `@pytest.mark.django_db` for tests that access the database:

```python
@pytest.mark.django_db
class TestAuditLibrary:
    def test_something(self):
        # Database access
        pass
```

### 2. Isolated Tests

- Each test must be independent
- Use factories to create necessary data
- Do not depend on test execution order

### 3. Descriptive Names

- Test names should clearly describe what is being tested
- Prefer: `test_slug_generation_automatic`
- Avoid: `test_1`, `test_library`

### 4. Clear Assertions

- Use `assert` with descriptive messages if necessary
- Test one behavior at a time

### 5. Reusable Factories

- Create factories for all models used in tests
- Use `SubFactory` for relationships
- Use `Faker` to generate realistic data

### 6. Relationship Tests

Test relationships between models (foreign keys, cascade deletes, etc.):

```python
def test_cascade_delete(self, organization):
    library = AuditLibraryFactory(organization=organization)
    library_id = library.id

    organization.delete()

    assert AuditLibrary.objects.filter(id=library_id).exists() is False
```

### 7. Integrity Tests

Test integrity constraints (unique, required, etc.):

```python
def test_unique_constraint(self):
    AuditLibraryFactory(name="Test")
    with pytest.raises(IntegrityError):
        AuditLibraryFactory(name="Test")
```

## Pytest Configuration

Pytest configuration is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "core.settings"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
```

## Complete Example

**Source code:**

```python
# audits/models/audit.py
from django.db import models

class AuditLibrary(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

**Factory:**

```python
# audits/tests/factories.py
class AuditLibraryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuditLibrary

    name = Faker("catch_phrase")
    organization = factory.SubFactory(OrganizationFactory)
```

**Tests:**

```python
# audits/tests/models/test_audit.py
import pytest
from audits.models.audit import AuditLibrary
from audits.tests.factories import AuditLibraryFactory
from organization.tests.factories import OrganizationFactory

@pytest.fixture
def organization():
    return OrganizationFactory()

@pytest.mark.django_db
class TestAuditLibrary:
    def test_slug_generation_automatic(self, organization):
        library = AuditLibraryFactory(name="Audit Library", organization=organization)
        assert library.slug == "audit-library"

    def test_organization_foreign_key(self, organization):
        library = AuditLibraryFactory(organization=organization)
        assert library.organization == organization
        assert library in organization.audit_libraries.all()

    def test_cascade_delete(self, organization):
        library = AuditLibraryFactory(organization=organization)
        library_id = library.id
        organization.delete()
        assert AuditLibrary.objects.filter(id=library_id).exists() is False
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [Django Testing Best Practices](https://docs.djangoproject.com/en/stable/topics/testing/)
