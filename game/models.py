from django.db import models


#### USUARIS D'ADMINISTRACIO
class AdminUser(models.Model):
    email = models.CharField(max_length=300)
    passwd = models.CharField(max_length=300) # guardar md5



####
class Partida(models.Model):
    num_partida = models.IntegerField()

    date_creation = models.DateTimeField()
    date_start = models.DateTimeField(null=True)
    date_end = models.DateTimeField(null=True)

    status = models.CharField(max_length=20, default="INACTIVA") # INACTIVA, REGISTERING, COMPLETA, ENJOC, ACABADA

    experiment = models.CharField(max_length=100, null=True) # Per marcar aquelles partides invalides

    num_rondes = models.IntegerField(null=True)
    ronda_actual = models.IntegerField(null=True)
    ronda_final = models.IntegerField(null=True)
    data_fi_ronda = models.DateTimeField(null=True)

    usuaris_registrats = models.IntegerField(default=0)

    # Varibles de control
    control_intervention = models.CharField(max_length=10, null=False, default='NONE') # NONE, HIGH, LOW, BOTH, EMERGE
    control_wealth = models.CharField(max_length=10, null=False, default='EQUAL') # EQUAL vs UNEQUAL

    comentari = models.CharField(max_length=100, null=True) # Per marcar aquelles partides invalides

    goal_achieved = models.BooleanField(default=False)
    total_contributed = models.FloatField(null=True)

class User(models.Model):
    is_robot = models.BooleanField(default=False)

    # Initial survey
    nickname = models.CharField(max_length=100, default="")
    consent = models.BooleanField(default=False)

    # Sociodemographic
    socio_pr1 = models.CharField(max_length=2, default="")
    socio_pr2 = models.CharField(max_length=2, default="")
    socio_pr3 = models.CharField(max_length=10, default="")
    socio_pr4 = models.CharField(max_length=2, default="")
    socio_pr5 = models.CharField(max_length=2, default="")
    socio_pr6 = models.CharField(max_length=2, default="")
    socio_pr7 = models.CharField(max_length=2, default="")

    # Framing
    frame_pr1 = models.CharField(max_length=2, default="")
    frame_pr2 = models.CharField(max_length=2, default="")
    frame_pr3 = models.CharField(max_length=2, default="")
    frame_pr4 = models.CharField(max_length=2, default="")
    frame_pr5 = models.CharField(max_length=2, default="")
    frame_pr6 = models.CharField(max_length=2, default="")

    # Verification
    verification_pr1 = models.CharField(max_length=100, default="")
    verification_pr2 = models.CharField(max_length=100, default="")
    verification_pr3 = models.CharField(max_length=100, default="")
    verification_pr4 = models.CharField(max_length=100, default="")
    verification_attempts = models.IntegerField(default=0)

    # Final survey
    enquesta_final_pr1 = models.CharField(max_length=100, default="")
    enquesta_final_pr2 = models.CharField(max_length=100, default="")
    enquesta_final_pr3 = models.CharField(max_length=100, default="")
    enquesta_final_pr4 = models.CharField(max_length=100, default="")
    enquesta_final_pr5 = models.CharField(max_length=100, default="")
    enquesta_final_pr6 = models.CharField(max_length=100, default="")

    ####################
    partida = models.ForeignKey(Partida, null=True)

    status = models.CharField(max_length=100, default="")

    num_jugador = models.IntegerField(null=True)

    date_tutorial = models.DateTimeField(null=True)
    date_register = models.DateTimeField(null=True)
    date_creation = models.DateTimeField(null=True)
    date_end = models.DateTimeField(null=True)

    acabat = models.BooleanField(default=False)
    num_seleccions = models.IntegerField(default=0)
    bots = models.IntegerField(default=0)

    endowment_initial = models.FloatField(default=0,null=True)
    endowment_current = models.FloatField(default=0,null=True)
    endowment_final = models.FloatField(default=0,null=True)

    expenses = models.FloatField(default=0,null=True)
    tickets = models.IntegerField(default=0,null=True)

    house = models.BooleanField(default=False)
    house_price = models.FloatField(null=True)

    comment = models.CharField(max_length=1000, default="")


class Ronda(models.Model):
    partida = models.ForeignKey(Partida)
    num_ronda = models.IntegerField()

    bucket_inici_ronda = models.FloatField(null=True)
    bucket_final_ronda = models.FloatField(null=True)

    temps_inici_ronda = models.DateTimeField(null=True)
    temps_final_ronda = models.DateTimeField(null=True)

    calculada = models.BooleanField(default=False)
    rented = models.BooleanField(default=False)
    increment = models.FloatField(null=True)

    user = models.ForeignKey(User, null=True)


class UserRonda(models.Model):
    ronda = models.ForeignKey(Ronda)
    user = models.ForeignKey(User, null=True)

    ha_seleccionat = models.BooleanField(default=False)
    seleccio = models.IntegerField(null=True)
    temps_seleccio = models.DateTimeField(null=True)

    endowment_variation = models.FloatField(null=True, default=0)

