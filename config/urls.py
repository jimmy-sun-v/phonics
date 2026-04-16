"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import include, path

from apps.speech.dashboard_views import diagnostics_dashboard_view


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", lambda request: redirect("phonics:category-list-page")),
    path("health/", health_check, name="health-check"),
    path("admin/", admin.site.urls),
    path("diagnostics/", diagnostics_dashboard_view, name="diagnostics-dashboard"),
    # Template (page) views
    path("phonics/", include("apps.phonics.page_urls")),
    path("games/", include("apps.games.page_urls")),
    # API views
    path("api/phonics/", include("apps.phonics.urls")),
    path("api/sessions/", include("apps.sessions.urls")),
    path("api/speech/", include("apps.speech.urls")),
    path("api/ai-tutor/", include("apps.ai_tutor.urls")),
    path("api/games/", include("apps.games.urls")),
]
