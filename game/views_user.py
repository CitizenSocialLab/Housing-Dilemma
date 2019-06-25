from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import *

from django import forms
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator

from django.utils import timezone

from game.models import *
from game.vars import *

import numpy as np

import math


####################
# USER STATUS
####################

def user_exists_in_db(user):
    try:
        User.objects.get(pk=user.id)
        return True
    except:
        return False

#######################
#### Initial Modul ####
#######################

## Interface Index
@csrf_exempt
def index(request, **kwargs):
    # Check valid user in the session
    if 'user' in request.session and request.session['user'] is not None:
        user = request.session['user']
        # Check valid user in the db
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')

    return redirect('user.nickname')

## Interface Nickname
class NicknameForm(forms.Form):
    nickname = forms.CharField(max_length=300)

@csrf_exempt
def nickname(request, **kwargs):
    # Check valid user in the session
    if 'user' in request.session and request.session['user'] is not None:
        user = request.session['user']
        # Check valid user in the db
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')
        #Todo: Distribute user when start
        if user_exists_in_db(user):
            if user.status == 'AVIS':
                return redirect('user.avis')
            elif user.status == 'SOCIODEMO':
                return redirect('user.survey1')
            elif user.status == 'FRAME':
                return redirect('user.frame')
            elif user.status == 'TUTORIAL_WAITING':
                return redirect('game.tutorial_inici')
            elif user.status == 'TUTORIAL':
                return redirect('game.tutorial')
            elif user.status == 'VERIFICATION':
                return redirect('user.verification')
            elif user.status == 'START':
                return redirect('user.inici')
            elif user.status == 'SURVEY_FINAL':
                return redirect('user.surveyfinal1')

    # Delete nickname
    if 'nickname' in request.session:
        del request.session['nickname']

    if request.method != 'POST':
        return render_to_response('nickname.html', {'lang': request.session['lang'], 'text': request.session['text']},
                                  context_instance=RequestContext(request))
    else:
        form = NicknameForm(request.POST)
        nick = form['nickname'].value()

        if not nick or len(nick) == 0:
            return render_to_response('nickname.html', {'lang': request.session['lang'], 'text': request.session['text']},
                                      context_instance=RequestContext(request))

        if len(nick) > 20:
            return render_to_response('nickname.html',
                                      {'nickname_error': False, 'nickname_error2': True, 'nickname': nick,
                                       'lang': request.session['lang'], 'text': request.session['text']},
                                      context_instance=RequestContext(request))

        # If the user exist distribute in the game or show an alert message
        #Todo: Distribute user when start or show a message
        try:
            user = User.objects.get(nickname=nick)
            request.session['user'] = user

            if user.status == 'AVIS':
                return redirect('user.avis')
            elif user.status == 'SOCIODEMO':
                return redirect('user.survey1')
            elif user.status == 'FRAME':
                return redirect('user.frame')
            elif user.status == 'TUTORIAL_WAITING':
                return redirect('game.tutorial_inici')
            elif user.status == 'TUTORIAL':
                return redirect('game.tutorial')
            elif user.status == 'VERIFICATION':
                return redirect('user.verification')
            elif user.status == 'START':
                return redirect('user.inici')
            elif user.status == 'SURVEY_FINAL':
                return redirect('user.surveyfinal1')
            else: return redirect('user.inici')

        # If user not exist send to survey
        except ObjectDoesNotExist:
            request.session['user'] = None
            request.session['nickname'] = nick

            user = User()
            user.date_creation = timezone.now()
            user.nickname = request.session['nickname']
            user.status = "AVIS"
            user.save()

            request.session['user'] = user
            return redirect('user.avis')
            #return redirect('user.survey1')


###########################
### Pantalla avis legal ###
###########################

class AvisForm(forms.Form):
    check_1 = forms.CharField(max_length=20)

@csrf_exempt
def avis(request, **kwargs):
    # Check valid user in the session
    if 'user' in request.session and request.session['user'] is not None:
        user = request.session['user']
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')
    else:
        return redirect('user.nickname')


    if request.method != 'POST':
        return render_to_response('avis.html',  {'lang': request.session['lang'], 'text': request.session['text']},
                              context_instance=RequestContext(request))
    else:
        form = AvisForm(request.POST)
        request.session['consent'] = True

        user = User.objects.get(id=request.session['user'].id)
        user.status = "SOCIODEMO"
        user.consent = request.session['consent']
        user.save()

        return redirect('user.survey1')

#########################
### Surveys Sociodemo ###
#########################

class SigninFormSurvey1(forms.Form):
    pr1 = forms.CharField(max_length=2)
    pr2 = forms.CharField(max_length=2)
    pr3 = forms.CharField(max_length=10)
    pr4 = forms.CharField(max_length=2)

@csrf_exempt
def survey1(request, **kwargs):

    # User validated in the session
    if 'user' in request.session and request.session['user'] is not None:
        user = User.objects.get(id=request.session['user'].id)
        user.status = 'Survey1'
        user.save()
        request.session['user'] = user
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')

    # Nickname in the session
    if 'nickname' not in request.session or request.session['nickname'] is None:
        return redirect('user.nickname')

    # ToDo: Control survey answered
    # Survey answered
    #if user.date_ended:
    #    return redirect('user.frame')

    # Post
    if request.method != 'POST':
        return render_to_response('survey1.html',
                                  {'lang': request.session['lang'],
                                   'text': request.session['text'],
                                   'user': user},
                                  context_instance=RequestContext(request))

    form = SigninFormSurvey1(request.POST)
    pr1 = form['pr1'].value()
    pr2 = form['pr2'].value()
    pr3 = form['pr3'].value()
    pr4 = form['pr4'].value()

    if not form.is_valid():
        return render_to_response('survey1.html', {
            'pr1': pr1,
            'pr1_danger': pr1 is None or len(pr1) == 0,
            'pr1_r1_checked': 'bx-option-selected' if pr1 == 'M' else '',
            'pr1_r2_checked': 'bx-option-selected' if pr1 == 'W' else '',
            'pr1_r3_checked': 'bx-option-selected' if pr1 == 'NB' else '',
            'pr1_r4_checked': 'bx-option-selected' if pr1 == 'NA' else '',

            'pr2': pr2,
            'pr2_danger': pr2 is None or len(pr2) == 0,
            'pr2_r1_checked': 'bx-option-selected' if pr2 == 'r1' else '',
            'pr2_r2_checked': 'bx-option-selected' if pr2 == 'r2' else '',
            'pr2_r3_checked': 'bx-option-selected' if pr2 == 'r3' else '',
            'pr2_r4_checked': 'bx-option-selected' if pr2 == 'r4' else '',
            'pr2_r5_checked': 'bx-option-selected' if pr2 == 'r5' else '',
            'pr2_r6_checked': 'bx-option-selected' if pr2 == 'r6' else '',
            'pr2_r7_checked': 'bx-option-selected' if pr2 == 'r7' else '',
            'pr2_r8_checked': 'bx-option-selected' if pr2 == 'r8' else '',

            'pr3': pr3,
            'pr3_danger': pr3 is None or len(pr3) == 0,

            'pr4': pr4,
            'pr4_danger': pr4 is None or len(pr4) == 0,
            'pr4_r1_checked': 'bx-option-selected' if pr4 == 'r1' else '',
            'pr4_r2_checked': 'bx-option-selected' if pr4 == 'r2' else '',
            'pr4_r3_checked': 'bx-option-selected' if pr4 == 'r3' else '',
            'pr4_r4_checked': 'bx-option-selected' if pr4 == 'r4' else '',
            'pr4_r5_checked': 'bx-option-selected' if pr4 == 'r5' else '',
            'pr4_r6_checked': 'bx-option-selected' if pr4 == 'r6' else '',

            'lang': request.session['lang'],
            'text': request.session['text'],
            'user': user,
        }, context_instance=RequestContext(request))

    else:
        request.session['pr1'] = pr1
        request.session['pr2'] = pr2
        request.session['pr3'] = pr3
        request.session['pr4'] = pr4

        user = User.objects.get(id=request.session['user'].id)

        user.socio_pr1 = request.session['pr1']
        user.socio_pr2 = request.session['pr2']
        user.socio_pr3 = request.session['pr3']
        user.socio_pr4 = request.session['pr4']

        print 'age: '+str(user.socio_pr2)
        if user.socio_pr2 == 'r1' or user.socio_pr2 == 'r2':
            user.comment += "MINOR "

        user.endowment_initial = 0
        user.endowment_current = 0
        user.status = "SURVEY2"

        user.save()

        request.session['user'] = user

        return redirect('user.survey2')


class SigninFormSurvey2(forms.Form):
    pr5 = forms.CharField(max_length=2)
    pr6 = forms.CharField(max_length=2)
    pr7 = forms.CharField(max_length=2)

@csrf_exempt
def survey2(request, **kwargs):

    # User validated in the session
    if 'user' in request.session and request.session['user'] is not None:
        user = User.objects.get(id=request.session['user'].id)
        user.status = 'Survey2'
        user.save()
        request.session['user'] = user
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')

    # Nickname in the session
    if 'nickname' not in request.session or request.session['nickname'] is None:
        return redirect('user.nickname')

    # ToDo: Control survey answered
    # Survey answered
    #if user.date_ended:
    #    return redirect('user.frame')

    # Post
    if request.method != 'POST':
        return render_to_response('survey2.html',
                                  {'lang': request.session['lang'],
                                   'text': request.session['text'],
                                   'user': user},
                                  context_instance=RequestContext(request))

    form = SigninFormSurvey2(request.POST)
    pr5 = form['pr5'].value()
    pr6 = form['pr6'].value()
    pr7 = form['pr7'].value()

    if not form.is_valid():
        return render_to_response('survey2.html', {
            'pr5': pr5,
            'pr5_danger': pr5 is None or len(pr5) == 0,
            'pr5_r1_checked': 'bx-option-selected' if pr5 == 'r1' else '',
            'pr5_r2_checked': 'bx-option-selected' if pr5 == 'r2' else '',
            'pr5_r3_checked': 'bx-option-selected' if pr5 == 'r3' else '',
            'pr5_r4_checked': 'bx-option-selected' if pr5 == 'r4' else '',

            'pr6': pr6,
            'pr6_danger': pr6 is None or len(pr6) == 0,
            'pr6_r1_checked': 'bx-option-selected' if pr6 == 'r1' else '',
            'pr6_r2_checked': 'bx-option-selected' if pr6 == 'r2' else '',
            'pr6_r3_checked': 'bx-option-selected' if pr6 == 'r3' else '',
            'pr6_r4_checked': 'bx-option-selected' if pr6 == 'r4' else '',
            'pr6_r5_checked': 'bx-option-selected' if pr6 == 'r5' else '',
            'pr6_r6_checked': 'bx-option-selected' if pr6 == 'r6' else '',
            'pr6_r7_checked': 'bx-option-selected' if pr6 == 'r7' else '',
            'pr6_r8_checked': 'bx-option-selected' if pr6 == 'r8' else '',

            'pr7': pr7,
            'pr7_danger': pr5 is None or len(pr7) == 0,
            'pr7_r1_checked': 'bx-option-selected' if pr7 == 'r1' else '',
            'pr7_r2_checked': 'bx-option-selected' if pr7 == 'r2' else '',
            'pr7_r3_checked': 'bx-option-selected' if pr7 == 'r3' else '',

            'lang': request.session['lang'],
            'text': request.session['text'],
            'user': user,
        }, context_instance=RequestContext(request))

    else:
        request.session['pr5'] = pr5
        request.session['pr6'] = pr6
        request.session['pr7'] = pr7

        user = User.objects.get(id=request.session['user'].id)

        user.socio_pr5 = request.session['pr5']
        user.socio_pr6 = request.session['pr6']
        user.socio_pr7 = request.session['pr7']

        user.status = "FRAME"

        user.save()

        request.session['user'] = user

        return redirect('user.frame')

#####################
### Surveys Frame ###
#####################

class SigninFormFrame(forms.Form):
    pr_framed1 = forms.CharField(max_length=2)
    pr_framed2 = forms.CharField(max_length=2)
    pr_framed3 = forms.CharField(max_length=2)

@csrf_exempt
def frame(request, **kwargs):
    # Check valid user in the session
    if 'user' in request.session and request.session['user'] is not None:
        user = request.session['user']
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')
    else:
        return redirect('user.nickname')

    # Check POST
    if request.method != 'POST':
        return render_to_response('frame.html',
                                  {'lang': request.session['lang'], 'text': request.session['text']},
                                  context_instance=RequestContext(request))

    form = SigninFormFrame(request.POST)
    frame_pr1 = form['pr_framed1'].value()
    frame_pr2 = form['pr_framed2'].value()
    frame_pr3 = form['pr_framed3'].value()

    if not form.is_valid():
        return render_to_response('frame.html', {

            'pr_framed1': frame_pr1,
            'pr_framed1_danger': frame_pr1 is None or len(frame_pr1) == 0,
            'pr_framed1_0_checked': 'bx-option-selected' if frame_pr1 == 'r1' else '',
            'pr_framed1_1_checked': 'bx-option-selected' if frame_pr1 == 'r2' else '',
            'pr_framed1_2_checked': 'bx-option-selected' if frame_pr1 == 'r3' else '',

            'pr_framed2': frame_pr2,
            'pr_framed2_danger': frame_pr2 is None or len(frame_pr2) == 0,
            'pr_framed2_0_checked': 'bx-option-selected' if frame_pr2 == 'r1' else '',
            'pr_framed2_1_checked': 'bx-option-selected' if frame_pr2 == 'r2' else '',
            'pr_framed2_2_checked': 'bx-option-selected' if frame_pr2 == 'r3' else '',

            'pr_framed3': frame_pr3,
            'pr_framed3_danger': frame_pr3 is None or len(frame_pr3) == 0,
            'pr_framed3_0_checked': 'bx-option-selected' if frame_pr3 == 'r1' else '',
            'pr_framed3_1_checked': 'bx-option-selected' if frame_pr3 == 'r2' else '',
            'pr_framed3_2_checked': 'bx-option-selected' if frame_pr3 == 'r3' else '',
            'lang': request.session['lang'], 'text': request.session['text']
        }, context_instance=RequestContext(request))


    else:
        request.session['pr_framed1'] = frame_pr1
        request.session['pr_framed2'] = frame_pr2
        request.session['pr_framed3'] = frame_pr3

    user = User.objects.get(id=request.session['user'].id)

    user.frame_pr1 = request.session['pr_framed1']
    user.frame_pr2 = request.session['pr_framed2']
    user.frame_pr3 = request.session['pr_framed3']

    user.status = "TUTORIAL_WAITING"

    request.session['user'] = user

    user.save()

    return redirect('user.frame2')


class SigninFormFrame2(forms.Form):
    pr_framed4 = forms.CharField(max_length=2)
    pr_framed5 = forms.CharField(max_length=2)
    pr_framed6 = forms.CharField(max_length=2)

@csrf_exempt
def frame2(request, **kwargs):
    # Check valid user in the session
    if 'user' in request.session and request.session['user'] is not None:
        user = request.session['user']
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')
    else:
        return redirect('user.nickname')

    # Check POST
    if request.method != 'POST':
        return render_to_response('frame2.html',
                                  {'lang': request.session['lang'],
                                   'text': request.session['text'],
                                   'municipi': MUNICIPI},
                                  context_instance=RequestContext(request))

    form = SigninFormFrame2(request.POST)
    frame_pr4 = form['pr_framed4'].value()
    frame_pr5 = form['pr_framed5'].value()
    frame_pr6 = form['pr_framed6'].value()

    if not form.is_valid():
        return render_to_response('frame2.html', {

            'pr_framed4': frame_pr4,
            'pr_framed4_danger': frame_pr4 is None or len(frame_pr4) == 0,
            'pr_framed4_0_checked': 'bx-option-selected' if frame_pr4 == 'r1' else '',
            'pr_framed4_1_checked': 'bx-option-selected' if frame_pr4 == 'r2' else '',
            'pr_framed4_2_checked': 'bx-option-selected' if frame_pr4 == 'r3' else '',
            'pr_framed4_3_checked': 'bx-option-selected' if frame_pr4 == 'r4' else '',
            'pr_framed4_4_checked': 'bx-option-selected' if frame_pr4 == 'r5' else '',
            'pr_framed4_5_checked': 'bx-option-selected' if frame_pr4 == 'r6' else '',
            'pr_framed4_6_checked': 'bx-option-selected' if frame_pr4 == 'r7' else '',
            'pr_framed4_7_checked': 'bx-option-selected' if frame_pr4 == 'r8' else '',

            'pr_framed5': frame_pr5,
            'pr_framed5_danger': frame_pr5 is None or len(frame_pr5) == 0,
            'pr_framed5_0_checked': 'bx-option-selected' if frame_pr5 == 'r1' else '',
            'pr_framed5_1_checked': 'bx-option-selected' if frame_pr5 == 'r2' else '',
            'pr_framed5_2_checked': 'bx-option-selected' if frame_pr5 == 'r3' else '',
            'pr_framed5_3_checked': 'bx-option-selected' if frame_pr5 == 'r4' else '',
            'pr_framed5_4_checked': 'bx-option-selected' if frame_pr5 == 'r5' else '',
            'pr_framed5_5_checked': 'bx-option-selected' if frame_pr5 == 'r6' else '',
            'pr_framed5_6_checked': 'bx-option-selected' if frame_pr5 == 'r7' else '',

            'pr_framed6': frame_pr6,
            'pr_framed6_danger': frame_pr6 is None or len(frame_pr6) == 0,
            'pr_framed6_0_checked': 'bx-option-selected' if frame_pr6 == 'r1' else '',
            'pr_framed6_1_checked': 'bx-option-selected' if frame_pr6 == 'r2' else '',
            'pr_framed6_2_checked': 'bx-option-selected' if frame_pr6 == 'r3' else '',
            'pr_framed6_3_checked': 'bx-option-selected' if frame_pr6 == 'r4' else '',
            'pr_framed6_4_checked': 'bx-option-selected' if frame_pr6 == 'r5' else '',
            'pr_framed6_5_checked': 'bx-option-selected' if frame_pr6 == 'r6' else '',
            'pr_framed6_6_checked': 'bx-option-selected' if frame_pr6 == 'r7' else '',

            'lang': request.session['lang'],
            'text': request.session['text'],
            'municipi': MUNICIPI,
        }, context_instance=RequestContext(request))


    else:
        request.session['pr_framed4'] = frame_pr4
        request.session['pr_framed5'] = frame_pr5
        request.session['pr_framed6'] = frame_pr6

    user = User.objects.get(id=request.session['user'].id)

    user.frame_pr4 = request.session['pr_framed4']
    user.frame_pr5 = request.session['pr_framed5']
    user.frame_pr6 = request.session['pr_framed6']

    user.status = "TUTORIAL_WAITING"

    request.session['user'] = user

    user.save()

    return redirect('game.tutorial_inici')

## Interfaces Verificacio
class SigninFormVerify(forms.Form):
    pr_verification1 = forms.CharField(max_length=100)
    pr_verification2 = forms.CharField(max_length=100)
    pr_verification3 = forms.CharField(max_length=100)
    pr_verification4 = forms.CharField(max_length=100)

@csrf_exempt
def verification(request, **kwargs):
    # Mirem si l'user ja esta validat a dins la sessio
    if 'user' in request.session and request.session['user'] is not None:
        user = request.session['user']
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')
    else:
        return redirect('user.nickname')

    user = User.objects.get(id=request.session['user'].id)
    user.status = 'VERIFICATION'
    user.save()

    # Mirem si ens estan ja retornant dades per validar o hem de mostrar l'enquesta
    if request.method != 'POST':
        return render_to_response('verification.html',
                                  {'lang': request.session['lang'], 'text': request.session['text']},
                                  context_instance=RequestContext(request))

    form = SigninFormVerify(request.POST)
    verification_pr1 = form['pr_verification1'].value()
    verification_pr2 = form['pr_verification2'].value()
    verification_pr3 = form['pr_verification3'].value()
    verification_pr4 = form['pr_verification4'].value()

    #ToDo: verification correct answer
    correct_answers = verification_pr1 == 'r2' and verification_pr2 == 'r1' and verification_pr3 == 'r1' and verification_pr4 == 'r2'
    if not correct_answers:
        user.verification_attempts += 1
        user.save()
    # correct_answers = True

    if not form.is_valid() or not correct_answers:
        return render_to_response('verification.html', {

            'pr_verification1': verification_pr1,
            'pr_verification1_danger': verification_pr1 is None or len(verification_pr1) == 0,
            'pr_verification1_0_checked': 'bx-option-selected' if verification_pr1 == 'r1' else '',
            'pr_verification1_1_checked': 'bx-option-selected' if verification_pr1 == 'r2' else '',

            'pr_verification2': verification_pr2,
            'pr_verification2_danger': verification_pr2 is None or len(verification_pr2) == 0,
            'pr_verification2_0_checked': 'bx-option-selected' if verification_pr2 == 'r1' else '',
            'pr_verification2_1_checked': 'bx-option-selected' if verification_pr2 == 'r2' else '',

            'pr_verification3': verification_pr3,
            'pr_verification3_danger': verification_pr3 is None or len(verification_pr3) == 0,
            'pr_verification3_0_checked': 'bx-option-selected' if verification_pr3 == 'r1' else '',
            'pr_verification3_1_checked': 'bx-option-selected' if verification_pr3 == 'r2' else '',

            'pr_verification4': verification_pr4,
            'pr_verification4_danger': verification_pr4 is None or len(verification_pr4) == 0,
            'pr_verification4_0_checked': 'bx-option-selected' if verification_pr4 == 'r1' else '',
            'pr_verification4_1_checked': 'bx-option-selected' if verification_pr4 == 'r2' else '',

            'pr_verification_error': not correct_answers,

            'lang': request.session['lang'], 'text': request.session['text']
        }, context_instance=RequestContext(request))


    else:
        request.session['pr_verification1'] = verification_pr1
        request.session['pr_verification2'] = verification_pr2
        request.session['pr_verification3'] = verification_pr3
        request.session['pr_verification4'] = verification_pr4

        user = User.objects.get(id=request.session['user'].id)

        user.verification_pr1 = request.session['pr_verification1']
        user.verification_pr2 = request.session['pr_verification2']
        user.verification_pr3 = request.session['pr_verification3']
        user.verification_pr4 = request.session['pr_verification4']
        user.status = "START"

        if user.verification_attempts >= 5:
            user.comment += "+4TRIES "

        user.save()

        return redirect('user.inici')

##################
### Game Modul ###
##################

## Logout game action
@csrf_exempt
def logout(request, **kwargs):
    if 'user' in request.session and request.session['user'] is not None:
        try:
            user = User.objects.get(pk=request.session['user'].id)
            user.status = 'Logout'
            user.save()
        except Exception as e:
            print e

        del request.session['user']
    return redirect('index')

## Start game action
@csrf_exempt
def inici(request, **kwargs):
    if 'user' not in request.session or request.session['user'] is None:
        print 'user not in request'
        return redirect('user.nickname')

    try:
        # Update the user information of the session
        print 'user in request and in database'
        user = User.objects.get(pk=request.session['user'].id)
        request.session['user'] = user
    except Exception as e:
        print 'user in request not in database'
        return redirect('user.nickname')

    #Todo: Message in Nickname that this user exist and choose a new nickname
    # User - END
    if user.date_end:
        print 'user end'
        return redirect('user.final_joc')

    # User - WITHOUT PARTIDA
    if not user.partida:
        print 'user no game'
        return  redirect('game.tutorial_inici')

    # User - WITHOUT REGISTER
    if not user.date_register:
        print 'user not registered'
        # Check POST
        if request.method != 'POST':
            return render_to_response('inici.html', {'user': user,
                                                     'lang': request.session['lang'],
                                                     'text': request.session['text'],
                                                     'error_partida':False,
                                                     'control_intervention_economic': user.partida.control_intervention == 'ECONOMIC',
                                                     'control_intervention_social': user.partida.control_intervention == 'SOCIAL'},
                                      context_instance=RequestContext(request))

        try:
            if user.partida.usuaris_registrats <= NUM_PLAYERS:
                print "Game ", user.partida.num_partida,"- Users Registered: ", user.partida.usuaris_registrats
                user.date_register = timezone.now()
                user.status = "REGISTERED"
                user.save()
            else:
                return redirect('user.tutorial_inici')

            # REGISTERED to GAME INDEX
            return redirect('game.index')
        except:
            # TRY AGAIN
            return redirect('user.inici')


        return render_to_response('inici.html', {'user': user,
                                                 'lang': request.session['lang'],
                                                 'text': request.session['text'],
                                                 'error_partida':True,
                                                 'control_intervention_economic': user.partida.control_intervention == 'ECONOMIC',
                                                 'control_intervention_social': user.partida.control_intervention == 'SOCIAL'},
                                  context_instance=RequestContext(request))


    # User REGISTERED
    else:
        print 'user registered'
        # User with GAME - REGISTERED and Game REGISTERING
        if user.partida and user.status == "REGISTERED" and user.partida.status == "REGISTERING":
            print 'user registered and game registering'
            return redirect('game.index')


        # User with GAME - REGISTERED and GAME PLAYING
        if user.partida and user.status == "REGISTERED" and user.partida.status == "PLAYING":
            print 'user registered and game playing'
            date_now = timezone.now()
            date_start = user.partida.date_start
            temps_actual_joc = (date_now - date_start).total_seconds()

            # Rounds DO NOT STARTED
            if temps_actual_joc < TEMPS_INICI_SEC:
                return redirect('game.index')

            # Rounds STARTED
            else :
                return redirect('user.inici')

        # User and Game PLAYING - But User EXIT GAME
        if user.partida and user.status == "PLAYING" and user.partida.status == "PLAYING":
            print 'You has quitted of the game and can not enter again.'
            #Todo: Send to results or nickname with a error message
            return redirect('user.resultats_clima')

        if user.partida and user.date_register and not user.date_end and user.partida.status == "REGISTERING":
            print 'player start and game registering'
            user = User.objects.get(id=request.session['user'].id)
            user.status = "REGISTERED"
            user.save()
            return redirect('game.index')

        if user.partida and (user.partida.status == "FINISHED" or user.partida.status == "FINISHED_MANUALLY"):
            return redirect('user.resultats_clima')


        return redirect('user.inici')

## Results game
@csrf_exempt
def resultats_clima(request, **kwargs):

    if 'user' not in request.session or request.session['user'] is None:
        return redirect('index')

    try:
        user = User.objects.get(pk=request.session['user'].id)
        request.session['user'] = user

    except Exception as e:
        return redirect('user.nickname')

    user.status = "RESULTS"
    user.save()

    return render_to_response('resultats_clima.html', {'lang': request.session['lang'],
                                                        'text': request.session['text'],
                                                        'user': request.session['user'],
                                                        'num_partida': request.session['user'].partida.num_partida},
                              context_instance=RequestContext(request))

## Final game
@csrf_exempt
def final_joc(request, **kwargs):
    if 'user' not in request.session or request.session['user'] is None:
        return redirect('index')

    try:
        # Update the user information of the session
        user = User.objects.get(pk=request.session['user'].id)
        user.status = "END"
        user.save()

        request.session['user'] = user

    except Exception as e:
        return redirect('user.nickname')

    #ToDo: Work in the last screen
    #del request.session['user']

    return render_to_response('final_joc.html', {'xAire': True if EXPERIMENT == 'xAire' else False,
                                                 'Athens': True if EXPERIMENT == 'Athens' else False,
                                                 'user': user,
                                                 'lang': request.session['lang'],
                                                 'text': request.session['text'],
                                                 'endowment_final': np.round(user.endowment_final,2),
                                                 'tickets': user.tickets,
                                                 'username': user.nickname,
                                                 'goal': "achieved" if user.partida.goal_achieved else "no_achieved",
                                                 'bot': user.bots
                                                 },
                              context_instance=RequestContext(request))

#####################
### Survey xAire  ###
#####################

@csrf_exempt
def enquestafinalintro(request, **kwargs):
    # Mirem si l'user ja esta validat a dins la sessio
    if 'user' not in request.session or request.session['user'] is None:
        return redirect('user.login')

    user = request.session['user']
    if not user_exists_in_db(user):
        del request.session['user']
        return redirect('user.login')

    # Mirem si ens estan ja retornant dades per validar o hem de mostrar l'enquesta
    return render_to_response('enquestafinalintro.html',
                                  {'lang': request.session['lang'],
                                   'text': request.session['text']},
                                  context_instance=RequestContext(request))

class SurveyFinalForm1(forms.Form):
    pr1 = forms.CharField(max_length=100)
    pr2 = forms.CharField(max_length=100)
    pr3 = forms.CharField(max_length=100)

@csrf_exempt
def surveyfinal1(request, **kwargs):

    # Check valid user in the session
    if 'user' in request.session and request.session['user'] is not None:
        user = request.session['user']
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')
    else:
        return redirect('user.nickname')

    if user.acabat:
        return redirect('user.final_joc')

    user = User.objects.get(id=request.session['user'].id)
    user.status = "SURVEY_FINAL"
    user.save()

    # Mirem si ens estan ja retornant dades per validar o hem de mostrar l'enquesta
    if request.method != 'POST':
        return render_to_response('surveyfinal1.html',
                                  {'lang': request.session['lang'], 'text': request.session['text']},
                                  context_instance=RequestContext(request))

    form = SurveyFinalForm1(request.POST)
    enquesta_final_pr1 = form['pr1'].value()
    enquesta_final_pr2 = form['pr2'].value()
    enquesta_final_pr3 = form['pr3'].value()


    if not form.is_valid():
        return render_to_response('surveyfinal1.html', {
            'pr1': enquesta_final_pr1,
            'pr1_danger': enquesta_final_pr1 is None or len(enquesta_final_pr1) == 0,
            'pr1_1_checked': 'bx-option-selected' if enquesta_final_pr1 == 'r1' else '',
            'pr1_2_checked': 'bx-option-selected' if enquesta_final_pr1 == 'r2' else '',
            'pr1_3_checked': 'bx-option-selected' if enquesta_final_pr1 == 'r3' else '',
            'pr1_4_checked': 'bx-option-selected' if enquesta_final_pr1 == 'r4' else '',
            'pr1_5_checked': 'bx-option-selected' if enquesta_final_pr1 == 'r5' else '',
            'pr1_6_checked': 'bx-option-selected' if enquesta_final_pr1 == 'r6' else '',
            'pr1_7_checked': 'bx-option-selected' if enquesta_final_pr1 == 'r7' else '',
            'pr1_8_checked': 'bx-option-selected' if enquesta_final_pr1 == 'r8' else '',


            'pr2': enquesta_final_pr2,
            'pr2_danger': enquesta_final_pr2 is None or len(enquesta_final_pr2) == 0,
            'pr2_1_checked': 'bx-option-selected' if enquesta_final_pr2 == 'r1' else '',
            'pr2_2_checked': 'bx-option-selected' if enquesta_final_pr2 == 'r2' else '',
            'pr2_3_checked': 'bx-option-selected' if enquesta_final_pr2 == 'r3' else '',
            'pr2_4_checked': 'bx-option-selected' if enquesta_final_pr2 == 'r4' else '',
            'pr2_5_checked': 'bx-option-selected' if enquesta_final_pr2 == 'r5' else '',
            'pr2_6_checked': 'bx-option-selected' if enquesta_final_pr2 == 'r6' else '',
            'pr2_7_checked': 'bx-option-selected' if enquesta_final_pr2 == 'r7' else '',
            'pr2_8_checked': 'bx-option-selected' if enquesta_final_pr2 == 'r8' else '',

            'pr3': enquesta_final_pr3,
            'pr3_danger': enquesta_final_pr3 is None or len(enquesta_final_pr3) == 0,
            'pr3_1_checked': 'bx-option-selected' if enquesta_final_pr3 == 'r1' else '',
            'pr3_2_checked': 'bx-option-selected' if enquesta_final_pr3 == 'r2' else '',
            'pr3_3_checked': 'bx-option-selected' if enquesta_final_pr3 == 'r3' else '',
            'pr3_4_checked': 'bx-option-selected' if enquesta_final_pr3 == 'r4' else '',
            'pr3_5_checked': 'bx-option-selected' if enquesta_final_pr3 == 'r5' else '',
            'pr3_6_checked': 'bx-option-selected' if enquesta_final_pr3 == 'r6' else '',
            'pr3_7_checked': 'bx-option-selected' if enquesta_final_pr3 == 'r7' else '',
            'pr3_8_checked': 'bx-option-selected' if enquesta_final_pr3 == 'r8' else '',

            'lang': request.session['lang'], 'text': request.session['text']
        }, context_instance=RequestContext(request))

    else:
        request.session['pr1'] = enquesta_final_pr1
        request.session['pr2'] = enquesta_final_pr2
        request.session['pr3'] = enquesta_final_pr3

        return redirect('user.surveyfinal2')

class SurveyFinalForm2(forms.Form):
    pr4 = forms.CharField(max_length=100)
    pr5 = forms.CharField(max_length=100)
    pr6 = forms.CharField(max_length=100)

@csrf_exempt
def surveyfinal2(request, **kwargs):

    # Check valid user in the session
    if 'user' in request.session and request.session['user'] is not None:
        user = request.session['user']
        if not user_exists_in_db(user):
            del request.session['user']
            return redirect('user.nickname')
    else:
        return redirect('user.nickname')

    if user.acabat:
        return redirect('user.final_joc')

    # Mirem si ens estan ja retornant dades per validar o hem de mostrar l'enquesta
    if request.method != 'POST':
        return render_to_response('surveyfinal2.html',
                                  {'lang': request.session['lang'], 'text': request.session['text']},
                                  context_instance=RequestContext(request))

    form = SurveyFinalForm2(request.POST)
    enquesta_final_pr4 = form['pr4'].value()
    enquesta_final_pr5 = form['pr5'].value()
    enquesta_final_pr6 = form['pr6'].value()

    print form

    if not form.is_valid():
        return render_to_response('surveyfinal2.html', {

            'pr4': enquesta_final_pr4,
            'pr4_danger': enquesta_final_pr4 is None or len(enquesta_final_pr4) == 0,
            'pr4_1_checked': 'bx-option-selected' if enquesta_final_pr4 == 'r1' else '',
            'pr4_2_checked': 'bx-option-selected' if enquesta_final_pr4 == 'r2' else '',
            'pr4_3_checked': 'bx-option-selected' if enquesta_final_pr4 == 'r3' else '',
            'pr4_4_checked': 'bx-option-selected' if enquesta_final_pr4 == 'r4' else '',
            'pr4_5_checked': 'bx-option-selected' if enquesta_final_pr4 == 'r5' else '',
            'pr4_6_checked': 'bx-option-selected' if enquesta_final_pr4 == 'r6' else '',
            'pr4_7_checked': 'bx-option-selected' if enquesta_final_pr4 == 'r7' else '',
            'pr4_8_checked': 'bx-option-selected' if enquesta_final_pr4 == 'r8' else '',

            'pr5': enquesta_final_pr5,
            'pr5_danger': enquesta_final_pr5 is None or len(enquesta_final_pr5) == 0,
            'pr5_1_checked': 'bx-option-selected' if enquesta_final_pr5 == 'r1' else '',
            'pr5_2_checked': 'bx-option-selected' if enquesta_final_pr5 == 'r2' else '',
            'pr5_3_checked': 'bx-option-selected' if enquesta_final_pr5 == 'r3' else '',

            'pr6': enquesta_final_pr6,

            'lang': request.session['lang'], 'text': request.session['text']
        }, context_instance=RequestContext(request))

    else:
        request.session['pr4'] = enquesta_final_pr4
        request.session['pr5'] = enquesta_final_pr5
        request.session['pr6'] = enquesta_final_pr6

        user = User.objects.get(id=request.session['user'].id)

        user.enquesta_final_pr1 = request.session['pr1']
        user.enquesta_final_pr2 = request.session['pr2']
        user.enquesta_final_pr3 = request.session['pr3']
        user.enquesta_final_pr4 = request.session['pr4']
        user.enquesta_final_pr5 = request.session['pr5']
        user.enquesta_final_pr6 = request.session['pr6']

        user.acabat = True
        user.date_end = timezone.now()
        user.status = "SURVEY_FINAL"

        user.save()

        return redirect('user.resultats_clima')



