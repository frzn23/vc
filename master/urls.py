from django.conf.urls import url
from django.urls import path
from django.urls.conf import include
from master import views


urlpatterns = [
    path('', views.index, name="Home"),
    path('manage', views.manage, name="Manage"),
    path('manage/<int>', views.manage_int, name="Manage"),
    path('handle', views.handle, name="Handle"),
    path('comment/<id>', views.comment, name="Comment"),
    path('w/<id>', views.wait, name="Weight"),
    path('logout', views.out, name="LogOut"),
]
