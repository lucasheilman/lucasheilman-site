from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lists', views.lists, name='lists'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('new_user', views.new_user, name='new_user'),
    path('lists_game_page/<str:game_name>/', views.lists_game_page, name='lists_game_page'),
    path('configure_lists_game/<str:game_name>/', views.configure_lists_game, name='configure_lists_game')
]
