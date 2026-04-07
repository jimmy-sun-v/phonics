from django.urls import path

from apps.phonics import page_views

app_name = "phonics"

urlpatterns = [
    path("", page_views.category_list_view, name="category-list-page"),
    path("<str:category>/", page_views.phoneme_list_view, name="phoneme-list-page"),
    # Learning loop
    path("learn/<str:symbol>/listen/", page_views.listen_step_view, name="learning-listen"),
    path("learn/<str:symbol>/observe/", page_views.observe_step_view, name="learning-observe"),
    path("learn/<str:symbol>/repeat/", page_views.repeat_step_view, name="learning-repeat"),
    path("learn/<str:symbol>/practice/", page_views.practice_step_view, name="learning-practice"),
    path("learn/<str:symbol>/reinforce/", page_views.reinforce_step_view, name="learning-reinforce"),
]
