from django.shortcuts import render
from .models import Volontari, Disponibilita

def lista_volontari(request):
    volontari = Volontari.objects.all()
    return render(request, 'volontari.html', {'volontari': volontari})

def lista_disponibilita(request):
    disponibilita = Disponibilita.objects.all()
    return render(request, 'disponibilita.html', {'disponibilita': disponibilita})
