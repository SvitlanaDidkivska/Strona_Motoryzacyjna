from django.urls import path
from .views_newsletter import newsletter_subscribe

app_name = 'news'

urlpatterns = [
    path('subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
]
