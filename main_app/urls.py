from django.urls import path
from .views import image_recognition

urlpatterns = [
    path('', image_recognition, name='image_recognition'),
]
