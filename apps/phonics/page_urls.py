from django.urls import path

from apps.phonics import page_views

app_name = "phonics"

urlpatterns = [
    path("", page_views.category_list_view, name="category-list-page"),
    path("<str:category>/", page_views.phoneme_list_view, name="phoneme-list-page"),
]
