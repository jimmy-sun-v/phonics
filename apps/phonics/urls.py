from django.urls import path

from . import views

urlpatterns = [
    path("categories/", views.category_list, name="category-list"),
    path("phonemes/", views.phoneme_list, name="phoneme-list"),
    path("phonemes/<str:symbol>/", views.phoneme_detail, name="phoneme-detail"),
]
