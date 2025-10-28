from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView,SpectacularRedocView
from django.urls import path


urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name='schema'),
    path("swagger/", SpectacularSwaggerView.as_view(), name= "swagger"),
    path("redoc/", SpectacularRedocView.as_view(), name= "redoc"),
]