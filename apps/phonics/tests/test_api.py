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
        assert len(response.data) == 8

    def test_invalid_category(self, client):
        response = client.get("/api/phonics/phonemes/?category=invalid")
        assert response.status_code == 400

    def test_phoneme_detail(self, client):
        response = client.get("/api/phonics/phonemes/sh/")
        assert response.status_code == 200
        assert response.data["symbol"] == "sh"

    def test_phoneme_not_found(self, client):
        response = client.get("/api/phonics/phonemes/zzz/")
        assert response.status_code == 404

    def test_all_phonemes(self, client):
        response = client.get("/api/phonics/phonemes/")
        assert response.status_code == 200
        assert len(response.data) == 59
