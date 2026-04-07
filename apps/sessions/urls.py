from django.urls import path

from . import views

app_name = "learning_sessions"

urlpatterns = [
    path("", views.session_create, name="session-create"),
    path("<uuid:session_id>/", views.session_detail, name="session-detail"),
]
