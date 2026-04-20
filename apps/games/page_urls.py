from django.urls import path

from apps.games import page_views

app_name = "games"

urlpatterns = [
    path("", page_views.game_list_view, name="game-list"),
    path("sound_picture/<str:symbol>/", page_views.sound_picture_view, name="sound-picture"),
    path("beginning_sound/<str:symbol>/", page_views.beginning_sound_view, name="beginning-sound"),
    path("blend_builder/<str:symbol>/", page_views.blend_builder_view, name="blend-builder"),
    path("balloon_pop/<str:symbol>/", page_views.balloon_pop_view, name="balloon-pop"),
    path("story_builder/", page_views.story_builder_view, name="story-builder"),
]
