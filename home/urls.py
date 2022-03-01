from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from . import views

urlpatterns = [
    path('', views.index),
    path('about', views.about),
    path('order', views.order),
    path('contact', views.contact),
    path('track', views.track),
    path('dry-clean', views.dry_clean),
    path('place-order/<int:id>', views.order_info),
    path('feedback/<int:id>', views.feedback),
    path('cancel-order', views.cancel),
    path('dc', views.dc),
    path('place-order-phone/<int:id>', views.take_phone),
    path('take_pass', views.take_pass),
    path('forget-password', views.change_pass),
    path('order-auth/<int:id>', views.order_auth),
    path('panel', views.panel),
    path('my-orders', views.my_order),
    path('take-review', views.take_review),
    path('review/<int:id>', views.review_sep),
    path('logoutc', views.log_out),

]