from django.contrib import admin
from frontend.views import *
from accounts.views import  *
from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import  AdminLoginView
from django.views.static import serve

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^api/$', include('api.urls',)),
    re_path(r'^accounts/$', include('accounts.urls',)), 
]

