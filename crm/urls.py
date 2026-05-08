"""
URL configuration for pitzpal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", auth_views.LoginView.as_view(), name="login"),
    path(
        "login/",
        auth_views.LoginView.as_view(),
        name="login",
    ),
    path("signup/", views.signup_view, name="signup"),
    path("search/", views.search_users, name="search"),
    path("send/<int:user_id>/", views.send_request, name="send_request"),
    path("requests/", views.friend_requests, name="friend_requests"),
    path("accept/<int:request_id>/", views.accept_request, name="accept_request"),
    path("reject/<int:request_id>/", views.reject_request, name="reject_request"),
    path("friends/", views.friends_list, name="friends_list"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
