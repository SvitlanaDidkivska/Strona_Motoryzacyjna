from django.urls import path
from . import views
from . import views_account
from news.views_newsletter import newsletter_subscribe

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('cars/', views.cars, name='cars'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('account/', views.account, name='account'),
    path('user/<str:username>/', views_account.user_profile, name='user_profile'),
    path('user/<str:username>/toggle_watch/', views_account.toggle_watch, name='toggle_watch'),
    path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
]
