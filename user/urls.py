"""Home_Social_Network URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import messages, user_register, user_login, user_logout, news, profile, friends, chat_id, \
edit_profile, create_post

urlpatterns = [
    path("messages", messages, name="messages"),
    path("messages/chat/<int:id>", chat_id, name="chat_id"),
    path("news", news, name="news"),
    path("profile/<int:id>", profile, name="profile"),
    path("register", user_register, name="register"),
    path("login", user_login, name="login"),
    path("create_post/", create_post, name="create_post"),
    path("friends/", friends, name="friends"),
    path("logout", user_logout, name="user_logout"),
    path("edit_profile", edit_profile, name="edit_profile")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)