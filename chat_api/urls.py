
from django.contrib import admin
from django.urls import path,include
from openapi.schema import urlpatterns as doc_urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/chat/", include("chat.urls")),
]+doc_urls



