from django.contrib import admin
from django.urls import path, include, reverse
from rest_framework_nested import routers

from . import views

app_name = 'core'

router = routers.DefaultRouter()
router.register('profile', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
] + router.urls

