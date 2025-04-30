from django.db import models

class Volontari(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    telegram_username = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    n_start_cmd = models.IntegerField(default=0)
    n_reg_cmd = models.IntegerField(default=0)
    n_unkwn_cmd = models.IntegerField(default=0)
    n_txtAdmin_cmd = models.IntegerField(default=0)
    n_disp_cmd = models.IntegerField(default=0)
    n_myshift_cmd = models.IntegerField(default=0)
    n_allshift_cmd = models.IntegerField(default=0)
    n_cmdlist_cmd = models.IntegerField(default=0)

    class Meta:
        managed = False  # Non lascia Django creare/modificare questa tabella
        db_table = 'volontari'

class Disponibilita(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_id = models.BigIntegerField()
    giorno = models.DateField(blank=True, null=True)
    fascia = models.CharField(max_length=50, blank=True, null=True)
    nome_cognome = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'disponibilita'
