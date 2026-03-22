from django.urls import path
from django.urls import re_path
from . import views
from .views import * 

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', views.serve_video),
    path('', main_page, name="main_page"),
    path('about/', about_page, name="about_page"),
    path('contacts', contacts_page, name="contacts_page"),
    path('login/', login_page, name="login_page"),
    path('register/', register_page, name="register_page"),
    path('profil/<int:pk>/', profil_page, name="profil_page"),
    path('anime/<str:slug>/', anime_detail_page, name="anime_detail_page"),
    path('anime/', all_anime_page, name="all_anime_page"),
    path('characters/', characters_page, name="characters_page"),
    path('episode/<int:episode_id>/', episode_detail_page, name='episode_detail'),
    path('gg/', all_gg_page, name="all_gg_page"),
    path('bookmark/<str:slug>/<str:status>/', add_bookmark, name="add_bookmark"),
    path('reating/<str:slug>/<str:point>/', add_reating, name="add_reating"),
    path('redact/', redact_page, name="redact_page"),
    path('save-progress/', views.save_progress, name='save_progress'),
    path('logout/', logout_view, name="logout"),
    path('comment/<str:slug>/', comment_action, name="comment_action"),
]
