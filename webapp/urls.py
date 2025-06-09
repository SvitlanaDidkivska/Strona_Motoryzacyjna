from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('main.urls', 'main'), namespace='main')),
    path('forum/', include(('forum.urls', 'forum'), namespace='forum')),
    path('news/', include('news.urls_newsletter', namespace='news')),
]
