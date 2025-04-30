from django.contrib import admin
from .models import Volontari, Disponibilita

@admin.register(Volontari)
class VolontariAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'first_name', 'last_name', 'telegram_username', 'created_at')
    search_fields = ('first_name', 'last_name', 'telegram_username', 'telegram_id')

@admin.register(Disponibilita)
class DisponibilitaAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'giorno', 'fascia', 'nome_cognome')
    search_fields = ('telegram_id', 'giorno', 'fascia', 'nome_cognome')
