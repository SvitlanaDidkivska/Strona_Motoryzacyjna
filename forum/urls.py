from django.urls import path
from . import views
from .views_post import add_post

app_name = 'forum'

urlpatterns = [
    path('', views.index, name='index'),
    path('add-post/', add_post, name='add_post'),
]
