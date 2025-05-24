from django.urls import path
from .views_newsletter import newsletter_subscribe

urlpatterns = [
    path('subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
]
