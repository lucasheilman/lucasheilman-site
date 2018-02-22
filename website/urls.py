from django.urls import path

from . import views

app_name = 'website'
urlpatterns = [
	path('<int:question_id>/vote/', views.vote, name='vote'),
    path('', views.index, name='index'),
    path('<int:question_id>/results/', views.results, name='results'),

    path('<int:question_id>/', views.detail, name='detail'),
]