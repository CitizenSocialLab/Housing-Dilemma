from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext
from django import forms

from game.models import *
from django.shortcuts import redirect
import random
from django.utils import timezone
from operator import itemgetter, attrgetter
from game.vars import *

import datetime

random.seed(datetime.datetime.now())

def create_intervention(users, game):

    # Sort users
    NUMS_PLAYERS_SORTED = sorted(NUMS_PLAYERS)

    users_sorted = users

    high_limit_agree = (len([u for u in users_sorted if u.frame_pr2 == 'r3']))
    high_limit_disagree = (len([u for u in users_sorted if u.frame_pr2 == 'r1']))
    high_control = high_limit_agree-high_limit_disagree

    print high_limit_agree
    print high_limit_disagree
    print high_control
    print '---'

    low_limit_agree = (len([u for u in users_sorted if u.frame_pr3 == 'r3']))
    low_limit_disagree = (len([u for u in users_sorted if u.frame_pr3 == 'r1']))
    low_control = low_limit_agree-low_limit_disagree

    print low_limit_agree
    print low_limit_disagree
    print low_control

    print '---'

    print 'High: ' +str(high_control)
    print 'Low: ' +str(low_control)

    if high_control > 0 and low_control > 0:
        game.control_intervention = 'BOTH'
    elif high_control > 0:
        game.control_intervention = 'HIGH'
    elif low_control > 0:
        game.control_intervention = 'LOW'
    elif high_control <= 0 and low_control <= 0:
        game.control_intervention = 'NONE'

    print 'Control: ' +str(game.control_intervention)

    for i in range(len(users_sorted)):
        users_sorted[i].num_jugador = NUMS_PLAYERS_SORTED[i]
        #usuaris_sorted[i].endowment_initial = VALUES[i]
        #usuaris_sorted[i].endowment_current = VALUES[i]
        users_sorted[i].save()

    return [users_sorted, game]

def pop_random(lst):
    idx = random.randrange(0, len(lst))
    return lst.pop(idx)

# Pantalla avis legal
class RegistreForm(forms.Form):
    control_wealth = forms.CharField()
    control_intervention = forms.CharField()

@csrf_exempt
def registre(request, **kwargs):

    partida_activa = Partida.objects.filter(status="REGISTERING")

    if len(partida_activa) > 0:

        # While registering and listing users
        partida_activa = partida_activa[0]
        usuaris = User.objects.filter(partida=partida_activa).filter(status='REGISTERED')

        # Registering and POST
        if request.method == 'POST':

                #ToDo: Controlling number of users
                if len(usuaris)==0:
                #if len(usuaris) < NUM_PLAYERS:
                    return redirect('admin.registre')

                form = RegistreForm(request.POST)
                #ToDo: Control wealth and Intervention
                control_wealth = form['control_wealth'].value()
                control_intervention = form['control_intervention'].value()

                partida_activa.control_wealth = control_wealth
                partida_activa.control_intervention = control_intervention

                partida_activa.status = "GENERATING DATA"
                partida_activa.save()

                if len(usuaris)<6:
                    # Creating bots
                    for i in range(6-len(usuaris)):
                        user = User()
                        user.is_robot = True
                        user.nickname = "BOT "+str(i+1)
                        user.socio_pr1 = "N"
                        user.socio_pr2 = -1
                        user.socio_pr3 = "N"
                        user.endowment_initial = 0
                        user.endowment_current = 0
                        user.date_creation = timezone.now()
                        user.partida = partida_activa
                        user.socio_pr4 = 0
                        user.frame_pr1 = 'r'+str(random.randrange(1, 3, 1))
                        user.frame_pr2 = 'r'+str(random.randrange(1, 3, 1))
                        user.frame_pr3 = 'r'+str(random.randrange(1, 3, 1))
                        user.status = "REGISTERED"
                        user.comment += "BOT "
                        user.save()
                    usuaris = User.objects.filter(partida=partida_activa).filter(status='REGISTERED')

                # Randomly assign NUMBER OF PLAYER
                random.shuffle(NUMS_PLAYERS)
                # Randomly assign ENDOWMENTS (control_wealth = "UNEQUAL")
                random.shuffle(ENDOWMENTS_UNEQUAL)

                # Equal endowments
                if partida_activa.control_wealth == 'EQUAL':
                    for i in range(len(usuaris)):
                        usuaris[i].num_jugador = NUMS_PLAYERS[i]
                        usuaris[i].endowment_initial = ENDOWMENTS_EQUAL[i]
                        usuaris[i].endowment_current = ENDOWMENTS_EQUAL[i]
                        usuaris[i].save()

                # Random Unequal endowments
                if partida_activa.control_wealth == 'UNEQUAL':
                    for i in range(len(usuaris)):
                        usuaris[i].num_jugador = NUMS_PLAYERS[i]
                        usuaris[i].endowment_initial = ENDOWMENTS_UNEQUAL[i]
                        usuaris[i].endowment_current = ENDOWMENTS_UNEQUAL[i]
                        usuaris[i].save()

                # Emerge from users endowments
                if partida_activa.control_intervention == 'EMERGE':
                    [usuaris, partida_activa] = create_intervention(usuaris, partida_activa)


                # Generating the data of the game
                partida_activa.num_rondes = NUM_ROUNDS
                for num_ronda in range(partida_activa.num_rondes):
                    ronda = Ronda.objects.create(partida=partida_activa, num_ronda=num_ronda+1)

                    for user in usuaris:
                        UserRonda.objects.create(user=user,
                                                 ronda=ronda,
                                                 ha_seleccionat=False)

                # Start the game
                partida_activa.status = "PLAYING"

                partida_activa.ronda_actual=1
                partida_activa.date_start = timezone.now()
                partida_activa.data_fi_ronda = timezone.now() + datetime.timedelta(seconds=TEMPS_INICI_SEC+TIME_ROUND_SEC)

                partida_activa.save()

                ronda_actual = partida_activa.ronda_set.get(num_ronda=1)
                ronda_actual.bucket_inici_ronda = HOUSING_PRICE
                ronda_actual.temps_inici_ronda = partida_activa.date_start + datetime.timedelta(seconds=TEMPS_INICI_SEC)
                ronda_actual.save()

                return redirect('admin.partida')

        print partida_activa.control_intervention
        # No POST - List of REGISTERED users
        return render_to_response('admin_registre.html',
                                  {'registre_iniciat': True,
                                                        'usuaris': usuaris,
                                                        'partida': partida_activa,
                                                        'pagina': 'registre',
                                                        'control_wealth': partida_activa.control_wealth,
                                                        'control_intervention': partida_activa.control_intervention,
                                                        'control_wealth_0_checked': 'bx-option-selected' if partida_activa.control_wealth == 'EQUAL' else '',
                                                        'control_wealth_1_checked': 'bx-option-selected' if partida_activa.control_wealth == 'UNEQUAL' else '',
                                                        'control_wealth_2_checked': 'bx-option-selected' if partida_activa.control_wealth == 'EMERGE' else '',

                                                        'control_intervention_0_checked': 'bx-option-selected' if partida_activa.control_intervention == 'NONE' else '',
                                                        'control_intervention_1_checked': 'bx-option-selected' if partida_activa.control_intervention == 'EMERGE' else '',
                                                        'control_intervention_2_checked': 'bx-option-selected' if partida_activa.control_intervention == 'HIGH' else '',
                                                        'control_intervention_3_checked': 'bx-option-selected' if partida_activa.control_intervention == 'LOW' else '',
                                                        'control_intervention_4_checked': 'bx-option-selected' if partida_activa.control_intervention == 'BOTH' else '',

                                                        'lang': request.session['lang'],
                                                        'text': request.session['text']},
                                  context_instance=RequestContext(request))


    # Opening a new Game
    if request.method == 'POST':
        results = Partida.objects.all().order_by('-num_partida')
        n_partida = 1
        #If there are more than one results, the last game number

        form = RegistreForm(request.POST)
        control_wealth = form['control_wealth'].value()
        control_intervention = form['control_intervention'].value()


        if not (control_intervention is None or len(control_intervention) == 0 or control_wealth is None or len(control_wealth) == 0):

            partida_activa.control_wealth = control_wealth
            partida_activa.control_intervention = control_intervention

            if len(results) > 0:
                n_partida = results[0].num_partida+1

            partida = Partida.objects.create(num_partida=n_partida,
                                             date_creation=timezone.now(),
                                             control_intervention=control_intervention,
                                             control_wealth=control_wealth,
                                             status="REGISTERING",
                                             experiment=EXPERIMENT,
                                             num_rondes=NUM_ROUNDS)
            partida.save()

        return redirect('admin.registre')

    # No POST - Waiting to open a new register
    return render_to_response('admin_registre.html',
                              {'registre_iniciat': False,
                               'lang': request.session['lang'],
                               'pagina': 'registre',
                               'text': request.session['text']},
                              context_instance=RequestContext(request))

@csrf_exempt
def partida(request, **kwargs):
    #Si no hi ha partida jugant-se mostrar avis
    return render_to_response('admin_partida.html', {
                                'lang': request.session['lang'],
                                'pagina': 'partida',
                                'text': request.session['text']},
                                context_instance=RequestContext(request))

@csrf_exempt
def stats(request, **kwargs):
    #Sino es un post, ensenyem el boto per crear registre nou
    return render_to_response('admin_stats.html', {
                                'lang': request.session['lang'],
                                'pagina': 'stats',
                                'text': request.session['text']},
                                context_instance=RequestContext(request))

@csrf_exempt
def partida_detail(request, **kwargs):
    num_partida = kwargs.get('num_partida', None)

    #Si no hi ha partida jugant-se mostrar avis
    return render_to_response('admin_partida_detail.html', {
                                'lang': request.session['lang'],
                                'num_partida': num_partida,
                                'pagina': 'partida_detail',
                                'text': request.session['text']},
                                context_instance=RequestContext(request))

@csrf_exempt
def users(request, **kwargs):

    #ToDo: Button that delete the user if they leave de game once he/she is registered

    users = User.objects.filter(is_robot=False).order_by('-date_creation')

    users = [{'id': u.id,
              'nickname': u.nickname if u else '-',
              'user_status': u.status if u else '-',
              'partida': u.partida_id if u.partida else '-',
              'partida_status': u.partida.status if u.partida else '-',
              'endowment_initial': u.endowment_initial if u else '-',
              'endowment_current': u.endowment_current if u else '-',
              'goal': u.partida.goal_achieved if u.partida else '-',
              'contributed': u.partida.total_contributed if u.partida else '-',
              } for u in User.objects.filter(is_robot=False).order_by('-date_creation')]
    users = users[0:18]

    return render_to_response('admin_users.html', {
                                         'lang': request.session['lang'],
                                         'pagina': 'users',
                                         'text': request.session['text'],
                                         'users': users},
                          context_instance=RequestContext(request))

@csrf_exempt
def users_reset(request, **kwargs):
    user_id = kwargs.get('user_id', None)
    print "Reseting user", user_id
    if user_id is not None:
        user = User.objects.get(id=user_id)
        if user is not None:
            user.partida=None
            user.status="RESET"
            user.save()
    return redirect('admin.users')

@csrf_exempt
def partida_list(request, **kwargs):
    partides = [{'num_partida': p.num_partida,
                 'date_creation': p.date_creation,
                 'users': [{'nickname': u.nickname} for u in p.user_set.all()[0:2]]}
                for p in Partida.objects.filter(status__in=("FINISHED", "FINISHED_MANUALLY")).order_by('-date_end')[0:20]]
    partides_1 = partides[0:10]
    partides_2 = partides[10:20]
    return render_to_response('admin_partida_list.html', {
                                         'lang': request.session['lang'],
                                         'pagina': 'partida_list',
                                         'text': request.session['text'],
                                         'partides_1': partides_1,
                                         'partides_2': partides_2},
                          context_instance=RequestContext(request))


