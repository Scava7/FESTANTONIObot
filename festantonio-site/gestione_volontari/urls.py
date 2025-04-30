from django.urls import path
from . import views

urlpatterns = [
    path('volontari/', views.lista_volontari, name='lista_volontari'),
    path('disponibilita/', views.lista_disponibilita, name='lista_disponibilita'),
]
