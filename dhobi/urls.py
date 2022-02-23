from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.urls.conf import include


urlpatterns = [
    path('main-master/', admin.site.urls),
    path('', include('home.urls')),
    path('master/', include('master.urls')),
    path('delivery/', include('delivery.urls')),
    path('laundry-panel/', include('laundry.urls')),
]
