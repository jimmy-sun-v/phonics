from django.urls import path

from . import views
from .story_views import story_history_detail, story_history_list, story_turn

urlpatterns = [
    path("", views.game_list, name="game-list"),
    path("<int:pk>/", views.game_detail, name="game-detail"),
    path("for-phoneme/<str:symbol>/", views.games_for_phoneme, name="games-for-phoneme"),
    path("story/turn/", story_turn, name="story-turn"),
    path("story/history/", story_history_list, name="story-history-list"),
    path("story/history/<int:story_session_id>/", story_history_detail, name="story-history-detail"),
]
