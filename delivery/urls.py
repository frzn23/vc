from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from . import views

urlpatterns = [
    path('', views.index),
    path('status/<int:id>', views.status),
    path('comment/<int:id>', views.comment),
    path('login/', views.login_del),
    path('logout/', views.logout_del),
]
