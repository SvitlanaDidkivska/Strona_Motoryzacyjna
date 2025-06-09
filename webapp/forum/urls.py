from django.urls import path
from . import views
from . import views_post

app_name = 'forum'




urlpatterns = [
    path('', views.index, name='index'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('post/add/', views_post.add_post, name='add_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/reaction/', views_post.add_post_reaction, name='add_post_reaction'),
    path('comment/<int:comment_id>/reaction/', views.add_comment_reaction, name='add_comment_reaction'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('category/add/', views.add_category, name='add_category'),
    path('comment/image_upload/', views.comment_image_upload, name='comment_image_upload'),
    path('badges/', views.badge_list, name='badge_list'),
]
