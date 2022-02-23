from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from laundry import views

urlpatterns = [
    path('', views.index),
    path('more/<int:id>', views.more),
    path('login', views.signin),

]