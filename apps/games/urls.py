from django.urls import path

from . import views
from .story_views import story_turn

urlpatterns = [
    path("", views.game_list, name="game-list"),
    path("<int:pk>/", views.game_detail, name="game-detail"),
    path("for-phoneme/<str:symbol>/", views.games_for_phoneme, name="games-for-phoneme"),
    path("story/turn/", story_turn, name="story-turn"),
]
