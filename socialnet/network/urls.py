from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('feed/', views.feed, name='feed'),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/comments/', views.view_comments, name='view_comments'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/like/', views.add_like, name='add_like'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/start/<str:username>/', views.start_chat, name='start_chat'),
    path('activity/', views.activity_feed, name='activity_feed'),
    path('post/<int:post_id>/', views.view_post, name='view_post'),
]
