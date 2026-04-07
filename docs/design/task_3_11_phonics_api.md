# Design: Task 3.11 – Phonics REST API – List & Detail Endpoints

## Overview

Create DRF viewset and serializers for phonics categories and phonemes: list categories, list phonemes (filterable by category), and phoneme detail.

## Dependencies

- Task 3.1 (Phonics service)

## Detailed Design

### URL Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/phonics/categories/` | List all categories with counts |
| GET | `/api/phonics/phonemes/` | List all phonemes (filterable by `?category=`) |
| GET | `/api/phonics/phonemes/{symbol}/` | Get phoneme detail by symbol |

### Serializer

**File: `apps/phonics/serializers.py`**

```python
from rest_framework import serializers
from apps.phonics.models import Phoneme


class CategorySerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()


class PhonemeSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Phoneme
        fields = [
            "id",
            "symbol",
            "category",
            "category_display",
            "example_words",
            "display_order",
        ]
        read_only_fields = fields
```

### Views

**File: `apps/phonics/views.py`**

```python
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.phonics.serializers import CategorySerializer, PhonemeSerializer
from apps.phonics.services import (
    get_all_categories,
    get_phonemes_by_category,
    get_phoneme_detail,
)
from apps.phonics.models import Phoneme


@api_view(["GET"])
def category_list(request):
    """List all phoneme categories with counts."""
    categories = get_all_categories()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def phoneme_list(request):
    """List phonemes, optionally filtered by category."""
    category = request.query_params.get("category")
    if category:
        try:
            phonemes = get_phonemes_by_category(category)
        except ValueError:
            return Response(
                {"error": f"Invalid category: {category}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        phonemes = Phoneme.objects.all().order_by("category", "display_order")

    serializer = PhonemeSerializer(phonemes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def phoneme_detail(request, symbol):
    """Get a single phoneme by symbol."""
    phoneme = get_phoneme_detail(symbol)
    if phoneme is None:
        return Response(
            {"error": f"Phoneme '{symbol}' not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = PhonemeSerializer(phoneme)
    return Response(serializer.data)
```

### URLs

**File: `apps/phonics/urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.category_list, name="category-list"),
    path("phonemes/", views.phoneme_list, name="phoneme-list"),
    path("phonemes/<str:symbol>/", views.phoneme_detail, name="phoneme-detail"),
]
```

### DRF Configuration

Add to `INSTALLED_APPS` in `config/settings/base.py`:
```python
"rest_framework",
```

Add REST_FRAMEWORK default config:
```python
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}
```

### Sample API Responses

**GET /api/phonics/categories/**
```json
[
    {"value": "single_letter", "label": "Single Letter Sound", "count": 24},
    {"value": "digraph", "label": "Digraph", "count": 8},
    {"value": "blend", "label": "Blend", "count": 9},
    {"value": "long_vowel", "label": "Long Vowel Pattern", "count": 9},
    {"value": "r_controlled", "label": "R-Controlled Vowel", "count": 5},
    {"value": "diphthong", "label": "Diphthong", "count": 4}
]
```

**GET /api/phonics/phonemes/sh/**
```json
{
    "id": 26,
    "symbol": "sh",
    "category": "digraph",
    "category_display": "Digraph",
    "example_words": ["ship", "shop", "shell"],
    "display_order": 2
}
```

## Acceptance Criteria

- [ ] Categories endpoint returns 6 categories
- [ ] Phonemes filterable by `?category=digraph`
- [ ] Detail returns full phoneme with example words
- [ ] Invalid category → 400
- [ ] Unknown phoneme symbol → 404

## Test Strategy

**File: `apps/phonics/tests/test_api.py`**

```python
import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestPhonicsAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    def test_categories_list(self, client):
        response = client.get("/api/phonics/categories/")
        assert response.status_code == 200
        assert len(response.data) == 6

    def test_phonemes_by_category(self, client):
        response = client.get("/api/phonics/phonemes/?category=digraph")
        assert response.status_code == 200
        symbols = [p["symbol"] for p in response.data]
        assert "sh" in symbols

    def test_invalid_category(self, client):
        response = client.get("/api/phonics/phonemes/?category=invalid")
        assert response.status_code == 400

    def test_phoneme_detail(self, client):
        response = client.get("/api/phonics/phonemes/sh/")
        assert response.status_code == 200
        assert response.data["symbol"] == "sh"
        assert "example_words" in response.data

    def test_phoneme_not_found(self, client):
        response = client.get("/api/phonics/phonemes/zz/")
        assert response.status_code == 404
```
