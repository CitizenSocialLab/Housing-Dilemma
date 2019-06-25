from django.views.decorators.csrf import csrf_exempt

from game.models import *
from game.vars import *

import math

import numpy as np

import datetime
from django.utils import timezone

import json
from django.http import HttpResponse

import random
random.seed(datetime.datetime.now())

@csrf_exempt
def demanar_dades(request, **kwargs):
    user_id = kwargs.get('user_id', None)

    response_data={}
    playing = "false"
    user = None

    try:
        # partida que juga aquest usuari
        user = User.objects.get(id=user_id)
    except:
        print "The user "+str(user_id)+" do not exist."

    # status de la partida actual
    if user.partida.status == "PLAYING":
        other_players = user.partida.user_set.all().exclude(id=user_id).order_by('num_jugador')
        playing = "true"

        # Times
        date_now = timezone.now()
        date_start = user.partida.date_start+datetime.timedelta(0, TEMPS_INICI_SEC)
        time = (date_start - date_now).total_seconds() # control of time

        if time > 0:
            response_data["countdown_initial_time"] = time*1000
        else:
            response_data["countdown_initial_time"] = 0

        # Control calculation of each round
        # calculs_ronda.counter = 1

        # Game, Round and Player info
        response_data["round_number"] = 1
        response_data["initial_endowment"] = user.endowment_current
        response_data["num_player"] = user.num_jugador
        response_data["control_intervention"] = user.partida.control_intervention

        # Vars
        response_data["tax"] = TAX
        response_data["subsidy"] = SUBSIDY
        response_data["limit_high"] = LIMIT_HIGH
        response_data["limit_low"] = LIMIT_LOW
        response_data["increment"] = INCREMENT
        response_data["municipi"] = MUNICIPI
        response_data["time_round"] = TIME_ROUND
        response_data["time_wait"] = TIME_WAIT
        response_data["total_rounds"] = NUM_ROUNDS
        response_data["price"] = HOUSING_PRICE
        response_data["experiment"] = EXPERIMENT

    response_data["playing"] = playing

    return HttpResponse(json.dumps(response_data),content_type="application/json")

@csrf_exempt
def enviar_accio(request, **kwargs):
    user_id = kwargs.get('user_id', None)
    num_ronda = kwargs.get('ronda_id', None)
    result = kwargs.get('result', None)

    # Update de les dades. Falta controlar si hi ha errors
    userronda = UserRonda.objects.filter(user_id=user_id, ronda__num_ronda=num_ronda).order_by('-id')

    if len(userronda) > 0:
        if userronda[0].seleccio is None:
            userronda[0].ha_seleccionat = True
            userronda[0].seleccio = int(result)
            userronda[0].temps_seleccio = timezone.now()
            userronda[0].save()

            userronda[0].user.num_seleccions += 1
            userronda[0].user.save()

        response_data = {"saved":"ok"}
    else:
        response_data = {"saved":"error"}

    return HttpResponse(json.dumps(response_data),content_type="application/json")

@csrf_exempt
def calculs_ronda(partida_activa, num_ronda):

    # The game is FINISHED or FINISHED_MANUALLY
    if partida_activa.status == "FINISHED" or partida_activa.status == "FINISHED_MANUALLY":
        return

    current_time = timezone.now()

    # Closing current round (not a previous or posterior)
    if num_ronda != partida_activa.ronda_actual:
        return

    # Counter number of times we are entering in here
    # calculs_ronda.counter += 1
    # print "COUNTER: "+str(calculs_ronda.counter)

    print "FINISHING ROUND:", num_ronda

    partida_activa.ronda_actual += 1
    partida_activa.data_fi_ronda = current_time + datetime.timedelta(seconds=TIME_WAIT_SEC+TIME_ROUND_SEC)
    partida_activa.save()

    round_finished = partida_activa.ronda_set.get(num_ronda=partida_activa.ronda_actual-1)

    # Bots selection
    for ur in round_finished.userronda_set.all():
        if not ur.ha_seleccionat:
            if not ur.user.house: ur.user.bots += 1
            ur.user.status = "PLAYING"
            ur.user.save()
            if ur.user.house or not ur.user.is_robot: # User get house OR is not a robot
                ur.seleccio = 0
            elif ur.user.is_robot: # User get no house AND is a robot
                ur.seleccio = random.randint(0,1)
            ur.temps_seleccio = current_time + timezone.timedelta(seconds=random.uniform(0,6))
            ur.save()

    # Selections by:
    # - Users without house
    # - Users selected to rent
    # - Sorted by selection time
    selections = round_finished.userronda_set.all().filter(user__house=False).filter(seleccio=1).order_by('temps_seleccio')
    selections_all = round_finished.userronda_set.all().order_by('temps_seleccio')
    print 'CALCULATING ROUND: '+str(num_ronda)
    # In case someone rent a house
    if len(selections) > 0:
        selections[0].user.endowment_current = selections[0].user.endowment_current - selections[0].ronda.bucket_inici_ronda
        selections[0].user.status = "PLAYING"
        selections[0].user.house = True
        selections[0].user.house_price = selections[0].ronda.bucket_inici_ronda
        selections[0].endowment_variation = - selections[0].ronda.bucket_inici_ronda

        try:
            round_previous_finished = partida_activa.ronda_set.get(num_ronda=partida_activa.ronda_actual-2)
            if partida_activa.control_intervention == 'BOTH' or partida_activa.control_intervention == 'LOW':
                if round_previous_finished:
                    if round_previous_finished.increment == 0 and round_previous_finished.rented == 0:
                        # Add subsidy
                        print '---- Add SUBSIDY'
                        selections[0].user.endowment_current = selections[0].user.endowment_current + SUBSIDY
                        selections[0].endowment_variation = - selections[0].ronda.bucket_inici_ronda + SUBSIDY
                        # Decrement TAX all participants
                        for s in selections_all:
                            if s.user.id != selections[0].user.id:
                                s.user.endowment_current -= TAX
                                s.endowment_variation = -TAX
                                s.user.save()
                                s.save()
        except:
            print 'No rounds'

        selections[0].user.save()
        selections[0].save()

        print "FINISHED ROUND:", partida_activa.ronda_actual

        # increment
        up = float(round_finished.bucket_inici_ronda * INCREMENT)/100

        if partida_activa.control_intervention == 'NONE' or \
            partida_activa.control_intervention == 'LOW' or \
            partida_activa.control_intervention == 'HIGH' and round_finished.bucket_inici_ronda + up < LIMIT_HIGH or \
            partida_activa.control_intervention == 'BOTH' and round_finished.bucket_inici_ronda + up < LIMIT_HIGH:

            round_finished.bucket_final_ronda = float(round_finished.bucket_inici_ronda + up)
            round_finished.increment = 1

        # equal
        elif partida_activa.control_intervention == 'HIGH' and round_finished.bucket_inici_ronda + up >= LIMIT_HIGH or \
            partida_activa.control_intervention == 'BOTH' and round_finished.bucket_inici_ronda + up >= LIMIT_HIGH:

            round_finished.bucket_final_ronda = round_finished.bucket_inici_ronda
            round_finished.increment = 0

        round_finished.user = selections[0].user
        round_finished.rented = True

        # once get house
        user_rounds = UserRonda.objects.filter(user=selections[0].user)
        for ur in user_rounds:
            if ur.seleccio is None:
                ur.seleccio = 0
                #ur.ha_seleccionat = True
                #ur.temps_seleccio = current_time
                ur.save()

    else:
        # decrement
        down = float(round_finished.bucket_inici_ronda * INCREMENT)/100

        if partida_activa.control_intervention == 'NONE' or \
            partida_activa.control_intervention == 'HIGH' or \
            partida_activa.control_intervention == 'LOW' and round_finished.bucket_inici_ronda - down > LIMIT_LOW or \
            partida_activa.control_intervention == 'BOTH' and round_finished.bucket_inici_ronda - down > LIMIT_LOW:

            round_finished.bucket_final_ronda = float(round_finished.bucket_inici_ronda - down)
            round_finished.increment = -1

        elif partida_activa.control_intervention == 'LOW' and round_finished.bucket_inici_ronda - down <= LIMIT_LOW or \
            partida_activa.control_intervention == 'BOTH' and round_finished.bucket_inici_ronda - down <= LIMIT_LOW:

            round_finished.bucket_final_ronda = round_finished.bucket_inici_ronda
            round_finished.increment = 0

        round_finished.rented = False

    round_finished.temps_final_ronda = current_time
    round_finished.calculada = True
    round_finished.save()


    # Check if all houses are rented
    all_houses_rented = True if len(round_finished.userronda_set.all().filter(user__house=True)) == 6 else False

    # If all rounds played or all house rented finish the game
    if partida_activa.ronda_actual > partida_activa.num_rondes or all_houses_rented:
        # Check if all houses are rented
        if (all_houses_rented):
            partida_activa.goal_achieved = True

        # calculation final results
        users = User.objects.filter(partida_id=partida_activa).filter(house=1).order_by('house_price')
        for index, u in enumerate(users):
            u.endowment_final = u.endowment_current
            u.expenses = u.endowment_initial - u.endowment_current

            # Check if the goal is achieved
            if u.house:
                if index < 2:
                    u.tickets = 6
                    print '6 :' + str(u.id)
                else:
                    u.tickets = 3
                    print '3 :' + str(u.id)
            else:
                u.tickets = 0
                print '0 :' + str(u.id)

            # Check the number of bots no wins no tickets
            if u.bots >= 2:
                u.comment += "BOTS "
                u.tickets = 0
                u.endowment_final = 0
            u.save()

        rondes = Ronda.objects.filter(partida_id=partida_activa).order_by('num_ronda')
        partida_activa.ronda_final = num_ronda
        partida_activa.total_contributed = np.mean([r.bucket_inici_ronda for r in rondes if r.rented == 1])
        partida_activa.status = "FINISHED"
        partida_activa.date_end = timezone.now()
        partida_activa.save()

    # Next round
    else:

        ronda_seguent = partida_activa.ronda_set.get(num_ronda=partida_activa.ronda_actual)
        ronda_seguent.bucket_inici_ronda = round_finished.bucket_final_ronda
        ronda_seguent.temps_inici_ronda = current_time + datetime.timedelta(seconds=TIME_WAIT_SEC)
        ronda_seguent.save()

@csrf_exempt
def demanar_resultat(request, **kwargs):
    user_id = kwargs.get('user_id', None)
    num_ronda = kwargs.get('ronda_id', None)

    # The participant is playing?
    user_ronda = UserRonda.objects.filter(user_id=user_id, ronda__num_ronda=num_ronda).order_by('-id')
    if len(user_ronda) == 0:
        # The participant is not playing
        return HttpResponse(json.dumps({"correcte": False}), content_type="application/json")

    user_ronda = user_ronda[0]
    user = user_ronda.user
    partida_activa = user.partida

    # Current round is equal or lower than the participant's round
    # Is changing to the next round?
    if partida_activa.ronda_actual == user_ronda.ronda.num_ronda:

        # Refresh data of the current round
        temps_restant = (partida_activa.data_fi_ronda - timezone.now()).total_seconds()

        # Calculate the results of the round
        if temps_restant <= 0:
            calculs_ronda(partida_activa, partida_activa.ronda_actual)

        # All players have contribute
        else:
            num_players = User.objects.filter(partida=partida_activa, is_robot=False).count()
            num_respostes = UserRonda.objects.filter(seleccio__isnull=False, ronda__partida = partida_activa, ronda__num_ronda=num_ronda, user__is_robot=False).count()

            if num_players == num_respostes and int(partida_activa.ronda_actual) == int(num_ronda):
                print 'Trying to enter'

            # if num_players == num_respostes and int(partida_activa.ronda_actual) == int(num_ronda) and calculs_ronda.counter == int(num_ronda):
                print 'Entering'
                calculs_ronda(partida_activa, partida_activa.ronda_actual)


    # If game is not PLAYING return the data to the participants
    if partida_activa.status != "PLAYING":
        return HttpResponse(json.dumps({"correcte": True, "jugant": False}), content_type="application/json")

    # If round is finished
    if user_ronda.ronda.num_ronda < partida_activa.ronda_actual and user_ronda.ronda.calculada:
        user = user_ronda.user

        response_data = {}

        current_player = {
            "id_user": user_ronda.user.id,
            "selection": user_ronda.seleccio,
            "selection_done": user_ronda.ha_seleccionat,
            "house": user_ronda.user.house,
        }
        response_data["current_player"] = current_player

        players = {
            "player_id" : [ur.user.id for ur in user_ronda.ronda.userronda_set.all().order_by('user__num_jugador')],
            "player_num" : [ur.user.num_jugador for ur in user_ronda.ronda.userronda_set.all().order_by('user__num_jugador')],
            #"time" : [(ur.temps_seleccio - ur.ronda.temps_inici_ronda).total_seconds() for ur in user_ronda.ronda.userronda_set.all().order_by('user__num_jugador')],
            "selection": [ur.seleccio for ur in user_ronda.ronda.userronda_set.all().order_by('user__num_jugador')],
            "selection_done": [ur.ha_seleccionat for ur in user_ronda.ronda.userronda_set.all().order_by('user__num_jugador')],
            "house" : [ur.user.house for ur in user_ronda.ronda.userronda_set.all().order_by('user__num_jugador')],
            "selection_order" : np.array([(ur.temps_seleccio - ur.ronda.temps_inici_ronda).total_seconds() for ur in user_ronda.ronda.userronda_set.all().order_by('user__num_jugador')]).argsort().argsort().tolist() ,
        }
        response_data["players"] = players

        # Rounds active game rented
        rounds_rented = Ronda.objects.filter(partida=partida_activa, rented=True).order_by('-id')

        houses = {
            "player_id" : [r.user.id for r in rounds_rented.all()],
            "player_num" : [r.user.num_jugador for r in rounds_rented.all()],
            "rounds" : [r.num_ronda for r in rounds_rented.all()],
            "price": [r.bucket_inici_ronda for r in rounds_rented.all()],
        }
        response_data["houses"] = houses

        # Rounds active game rented
        current_round = Ronda.objects.filter(partida=partida_activa, num_ronda=int(num_ronda)).order_by('-id')
        selections_current_round = UserRonda.objects.filter(ronda=current_round[0])

        try:
            if len(current_round) > 0:
                selections_current_round = UserRonda.objects.filter(ronda=current_round[0])

                if len(selections_current_round) > 0:
                    total_price_accepted = len([scr for scr in selections_current_round if scr.seleccio == 1])

                round = {
                    "round_num": current_round[0].num_ronda,
                    "rented": int(current_round[0].rented),
                    "player_id": current_round[0].user.id if current_round[0].rented else '',
                    "player_num": current_round[0].user.num_jugador if current_round[0].rented else '',
                    "price_rented": current_round[0].bucket_inici_ronda,
                    "price_market": current_round[0].bucket_final_ronda,
                    "price_accepted": total_price_accepted,
                    "increment": current_round[0].increment,
                    "error": False
                }
        except:
            round = {"error": True}

        response_data["correcte"] = True
        response_data["playing"] = True if partida_activa.status == "PLAYING" else False

        response_data["current_round"] = round
        response_data["ronda_acabada"] = True
        response_data["house_rented"] = user.house
        response_data["numero_ronda"] = partida_activa.ronda_actual
        response_data["diners_inici_ronda"] = user.endowment_current
        response_data["temps_restant"] = (partida_activa.data_fi_ronda - timezone.now()).total_seconds() - TIME_ROUND_SEC,
        response_data["price_initial"] = user_ronda.ronda.bucket_inici_ronda
        response_data["price_final"] = user_ronda.ronda.bucket_final_ronda

        # Vars
        response_data["tax"] = TAX
        response_data["subsidy"] = SUBSIDY
        response_data["limit_high"] = LIMIT_HIGH
        response_data["limit_low"] = LIMIT_LOW
        response_data["increment"] = INCREMENT

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    else:
        return HttpResponse(json.dumps({"ronda_acabada": False}), content_type="application/json")

#################################
### WEBSERVICES ADMINISTRACIO ###
#################################

@csrf_exempt
def usuaris_registrats(request, **kwargs):
    response_data = {}

    partida_activa = Partida.objects.filter(status="REGISTERING")
    if len(partida_activa) > 0:
        response_data['registering'] = True

        partida_activa = partida_activa[0]

        all_users = []

        for usuari in User.objects.filter(partida=partida_activa):
            if usuari.date_tutorial is not None: date = usuari.date_tutorial.strftime("%a,  %d/%m/%Y - %H:%M:%S")
            if usuari.date_register is not None: date = usuari.date_register.strftime("%a,  %d/%m/%Y - %H:%M:%S")

            # Variables Treatment High Limit
            if usuari.frame_pr2 == 'r3':
                high = 'Yes :)'
            elif usuari.frame_pr2 == 'r1':
                high = 'No  :('
            else:
                high = 'Bah :()'

            # Variables Treatment Low Limit
            if usuari.frame_pr3 == 'r3':
                low = 'Yes :)'
            elif usuari.frame_pr3 == 'r1':
                low = 'No  :('
            else:
                low = 'Bah :()'

            data_users = {"id_user": usuari.id,
                          "id_game": usuari.partida.id,
                           "nom": usuari.nickname,
                           "status": usuari.status,
                           "low": low,
                           "high": high,
                           "date": date,
                           "verification": usuari.verification_attempts}

            all_users.append(data_users)
        response_data['usuaris'] = all_users

    else:
        response_data['registering'] = False

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def status_partida(request, **kwargs):
    response_data = {'partides': []}

    for partida in Partida.objects.filter(status="PLAYING"):

        #Info de la partida
        users = User.objects.filter(partida__num_partida = partida.num_partida)

        data = {'num_partida': partida.num_partida,
                'date_creation': partida.date_creation.strftime("%d/%m - %H:%M:%S"),
                'data_inici': partida.date_start.strftime("%d/%m - %H:%M:%S"),
                'treatment' : partida.control_wealth,
                }

        # Mirem si hem d'de tancar la ronda actual
        temps_restant = (partida.data_fi_ronda - timezone.now()).total_seconds()

        if temps_restant <= 0 and partida.ronda_actual <= partida.num_rondes:
            print ('calculs ronda I')
            calculs_ronda(partida, partida.ronda_actual)

        ronda_data = []
        for i in range(1, partida.ronda_actual+1):

            round_info = {}
            round_db = Ronda.objects.filter(partida=partida).filter(num_ronda=i)[0]
            round_info['ronda'] = i
            round_info['status'] = ''
            round_info['rented'] = False

            round_info['num_respostes'] = UserRonda.objects.filter(seleccio__isnull=False, ronda__partida = partida, ronda__num_ronda=i).count()
            round_info['num_jugadors'] = User.objects.filter(partida=partida).count()
            round_info['price'] = round_db.bucket_inici_ronda

            if round_db.calculada:
                round_info['status'] = 'ENDED'
                round_info['rented'] = round_db.rented

            elif i == partida.ronda_actual:
                round_info['status'] = 'PLAYING'

            ronda_data.append(round_info)

        data["ronda_data"] = ronda_data

        if partida.ronda_actual > partida.num_rondes:
            data['status'] = "Se han jugado todas las rondas"

        elif partida.ronda_actual == 1:
            if temps_restant > TIME_ROUND_SEC:
                data['status'] = "Game starts in "+str(int(round(temps_restant-TIME_ROUND_SEC)))+"s"
            else:
                data['status'] = "Round 1 ("+str(int(math.ceil(temps_restant)))+ "s)"

        else:
            if temps_restant > TIME_ROUND_SEC:
                data['status'] = "Results round "+str(partida.ronda_actual-1)+" ("\
                                         +str(int(round(temps_restant-TIME_ROUND_SEC)))+"s)"
            else :
                data['status'] = "Playing round "+str(partida.ronda_actual)+" ("\
                                         +str(int(math.ceil(temps_restant)))+ "s)"

        response_data['partides'].append(data)

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def tancar_ronda(request, **kwargs):

    response_data = {}
    num_partida = kwargs.get('num_partida', None)
    partida = Partida.objects.get(num_partida=num_partida)
    calculs_ronda(partida, partida.ronda_actual)

    response_data["correcte"] = False
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def tancar_partida(request, **kwargs):

    response_data = {}
    num_partida = kwargs.get('num_partida', None)
    partida = Partida.objects.get(num_partida=num_partida)
    if partida.status == "PLAYING":
        partida.status = "FINISHED_MANUALLY"
        partida.date_end = timezone.now()
        partida.save()

    response_data["correcte"] = False
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def llistat_partides(request, **kwargs):

    response_data = {}

    all_partides = []
    for partida in Partida.objects.filter().order_by('-id')[:15]:

        users = User.objects.filter(partida__num_partida = partida.num_partida)
        #print(partida.date_end)
        data_partida = {"num_partida": partida.num_partida,
                        "guanys": [up.tickets for up in users],
                        "goal_achieved": partida.goal_achieved,
                        "date_creation": partida.date_creation.strftime("%a, %H:%M:%S"),
                        "wealth": partida.control_wealth,
                        "reward": partida.control_intervention,
                        "date_end": partida.date_end.strftime("%a, %H:%M:%S") if partida.date_end else '-',
                        "status": partida.status
        }

        all_partides.append(data_partida)

    response_data["partida"] = all_partides

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def stats_partida(request, **kwargs):

    response_data = {}

    all_partides = []

    games = [p for p in Partida.objects.filter(status="FINISHED").filter(experiment=EXPERIMENT).order_by('-id')]
    participants = User.objects.filter(acabat=1)

    response_data["total_games"] = len(games)

    #Todo: Show information about the games and the typology
    response_data["total_games_economic"] = 0
    response_data["total_games_social"] = 0

    response_data["total_games_treatment_none"] = len([g for g in games if g.control_intervention == 'NONE'])
    response_data["total_games_treatment_low"] = len([g for g in games if g.control_intervention == 'LOW'])
    response_data["total_games_treatment_high"] = len([g for g in games if g.control_intervention == 'HIGH'])
    response_data["total_games_treatment_both"] = len([g for g in games if g.control_intervention == 'BOTH'])
    response_data["total_games_treatment_emerge"] = len([g for g in games if g.control_intervention == 'EMERGE'])

    response_data["total_games_achieved"] = len([g for g in games if g.goal_achieved])
    response_data["total_participants"] = len(participants)
    response_data["tickets_laie"] = sum([(p.tickets) for p in participants])
    response_data["tickets_valid"] = sum([(p.tickets) for p in participants if not p.comment == 'TEST'])
    response_data["valid_participants"] = (len([p for p in participants if p.comment == '']))

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def delete_user(request, **kwargs):

    response_data = {}
    id_user = kwargs.get('id_user', None)

    user = User.objects.get(id=id_user)

    # NO_VALID and NO_GAME
    user.partida.usuaris_registrats -= 1
    user.partida.save()
    user.status = 'NO_VALID'
    user.partida = None
    user.save()

    response_data["correcte"] = True

    return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def stats_partida_detail(request, **kwargs):

    # parameters URL
    num_partida = kwargs.get('num_partida', None)

    # database queries
    partida = Partida.objects.filter(num_partida=num_partida)[0]
    users_partida = User.objects.filter(partida_id=partida.id).order_by('num_jugador')
    rounds = Ronda.objects.filter(partida_id=partida.id).order_by('num_ronda')

    temps_restant = (partida.data_fi_ronda - timezone.now()).total_seconds()

    # status of games
    if partida.ronda_actual > partida.num_rondes:
        message_status = "All rounds played"

    elif partida.ronda_actual == 1:
        if temps_restant > TIME_ROUND_SEC:
            message_status = "Game starts in "+str(int(round(temps_restant-TIME_ROUND_SEC)))+"s"
        else:
            message_status = "Round 1 ("+str(int(math.ceil(temps_restant)))+ "s)"

    else:
        if temps_restant > TIME_ROUND_SEC:
            message_status = "Results round "+str(partida.ronda_actual-1)+" ("\
                                     +str(int(round(temps_restant-TIME_ROUND_SEC)))+"s)"
        else :
            message_status = "Playing round "+str(partida.ronda_actual)+" ("\
                                     +str(int(math.ceil(temps_restant)))+ "s)"


    if partida.date_end is None: dc = '-'
    else: dc = partida.date_end.strftime("%a,  %d/%m/%Y - %H:%M:%S")

    response_data = {
        "status_game": message_status,
        "num_partida": num_partida,
        "num_round": partida.ronda_actual,
        "num_players": NUM_PLAYERS,
        #"threshold": THRESHOLD,
        #"status_partida": partida.statucontrol_interventionways_control_interventionalways_win,
        "control_intervention": partida.control_intervention,
        "control_wealth": partida.control_wealth,
        "limit_high": LIMIT_HIGH,
        "limit_low": LIMIT_LOW,
        #"factor_return": FACTOR_RETURN,
        "guanys": [up.endowment_final for up in users_partida],
        "edad": [up.socio_pr2 for up in users_partida],
        "date_creacio": partida.date_creation.strftime("%a,  %d/%m/%Y - %H:%M:%S"),
        "date_inici": partida.date_start.strftime("%a,  %d/%m/%Y - %H:%M:%S"),
        "date_final": dc,
        "user_ids": [up.id for up in users_partida],
        #"nicknames": [up.nickname for up in users_partida],
        "endowment_initial": [up.endowment_initial for up in users_partida],
        "diners_contribuits": [up.endowment_initial - up.endowment_current for up in users_partida],
        "bots": [up.bots for up in users_partida],
        "endowment_final": [up.endowment_final for up in users_partida],
        "tickets": [up.tickets for up in users_partida],
    }

    # Rondes de tots els users de la partida
    user_ronda_seleccio = []
    robot_seleccio = []
    endowment_variation = []
    for up in users_partida:
        user_ronda =  UserRonda.objects.filter(user_id=up.id).order_by('ronda_id')
        user_ronda_seleccio.append([ur.seleccio for ur in user_ronda])
        robot_seleccio.append([ur.ha_seleccionat for ur in user_ronda])
        endowment_variation.append([ur.endowment_variation for ur in user_ronda])
    response_data["rondes"] = user_ronda_seleccio
    response_data["robot"] = robot_seleccio
    response_data["variation"] = endowment_variation

    # House data in rounds
    rounds_house = {
        'house_price': [round(r.bucket_inici_ronda) for r in rounds if r.bucket_inici_ronda is not None],
        'house_rented': [r.rented for r in rounds if r.bucket_inici_ronda is not None],
        'house_renter': [r.user_id for r in rounds if r.bucket_inici_ronda is not None],
        'house_price_increment': [r.increment for r in rounds if r.bucket_inici_ronda is not None],
        'house_price_average': 0,
    }

    rounds_house['house_price_average'] = round(np.nanmean(rounds_house['house_price']),1)

    response_data["rounds_house"] = rounds_house

    # Renter data in in rounds
    rounds_player = {
        'id_player': [],
        'nicknames': [],
        'house_price': [],
        'rented_round': [],
        'rent': [], # evolution of rent
        'selections': [],
        'is_robot': [],
        'rent_average': 0,
        'tickets': [],
    }



    for up in users_partida:
        user_ronda =  UserRonda.objects.filter(user_id=up.id).order_by('ronda_id')
        ronda = Ronda.objects.filter(user_id=up.id)
        rounds_player['id_player'].append(up.id)
        rounds_player['nicknames'].append(up.nickname)
        rounds_player['tickets'].append(up.tickets)
        rounds_player['house_price'].append(round(up.house_price) if up.house_price else '-')
        rounds_player['rented_round'].append(ronda[0].num_ronda if len(ronda) > 0 else '-')
        rounds_player['selections'].append([ur.seleccio for ur in user_ronda])
        rounds_player['is_robot'].append([ur.ha_seleccionat for ur in user_ronda])

        rent_player = [up.endowment_initial]
        for i in range(len(user_ronda)):
            rent_player.append(round(rent_player[i] + user_ronda[i].endowment_variation))

        rounds_player['rent'].append(rent_player)


    if len([r.bucket_inici_ronda for r in rounds if r.rented]) != 0:
        rounds_player['rent_average'] = np.nanmean([r.bucket_inici_ronda for r in rounds if r.rented])
    else:
        rounds_player['rent_average'] = 0

    response_data["rounds_player"] = rounds_player

    return HttpResponse(json.dumps(response_data), content_type="application/json")

