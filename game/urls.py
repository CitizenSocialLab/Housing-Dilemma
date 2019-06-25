from django.conf.urls import patterns, url

import views
import views_game
import views_user
import views_admin
import views_ws

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

     url(r'^((?P<lang>[\w-]+)/)?$', views.index, name='index'),

     url(r'^((?P<lang>[\w-]+)/)?user$', views_user.index),
     url(r'^((?P<lang>[\w-]+)/)?user/logout$', views_user.logout, name="user.logout"),

     url(r'^((?P<lang>[\w-]+)/)?user/nickname$', views_user.nickname, name="user.nickname"),
     url(r'^((?P<lang>[\w-]+)/)?user/avis$', views_user.avis, name="user.avis"),

     url(r'^((?P<lang>[\w-]+)/)?user/survey1$', views_user.survey1, name="user.survey1"),
     url(r'^((?P<lang>[\w-]+)/)?user/survey2$', views_user.survey2, name="user.survey2"),
     url(r'^((?P<lang>[\w-]+)/)?user/frame$', views_user.frame, name="user.frame"),
     url(r'^((?P<lang>[\w-]+)/)?user/frame2$', views_user.frame2, name="user.frame2"),
     url(r'^((?P<lang>[\w-]+)/)?user/verification$', views_user.verification, name="user.verification"),

     url(r'^((?P<lang>[\w-]+)/)?user/enquestafinalintro$', views_user.enquestafinalintro, name="user.enquestafinalintro"),
     url(r'^((?P<lang>[\w-]+)/)?user/surveyfinal1$', views_user.surveyfinal1, name="user.surveyfinal1"),
     url(r'^((?P<lang>[\w-]+)/)?user/surveyfinal2$', views_user.surveyfinal2, name="user.surveyfinal2"),

     url(r'^((?P<lang>[\w-]+)/)?user/inici', views_user.inici, name="user.inici"),
     url(r'^((?P<lang>[\w-]+)/)?user/resultats_clima', views_user.resultats_clima, name="user.resultats_clima"),
     url(r'^((?P<lang>[\w-]+)/)?user/final_joc', views_user.final_joc, name="user.final_joc"),

     url(r'^((?P<lang>[\w-]+)/)?game$', views_game.index, name='game.index'),
     url(r'^((?P<lang>[\w-]+)/)?game/tutorial$', views_game.tutorial, name='game.tutorial'),
     url(r'^((?P<lang>[\w-]+)/)?game/tutorial_inici$', views_game.tutorial_inici, name='game.tutorial_inici'),
     url(r'^((?P<lang>[\w-]+)/)?game/logos', views_game.logos, name="game.logos"),

     url(r'^((?P<lang>[\w-]+)/)?admin$', views_admin.registre, name='admin.admin'),
     url(r'^((?P<lang>[\w-]+)/)?admin/registre$', views_admin.registre, name='admin.registre'),
     url(r'^((?P<lang>[\w-]+)/)?admin/partida$', views_admin.partida, name='admin.partida'),
     url(r'^((?P<lang>[\w-]+)/)?admin/stats$', views_admin.stats, name='admin.stats'),
     url(r'^((?P<lang>[\w-]+)/)?admin/users$', views_admin.users, name='admin.users'),
     url(r'^((?P<lang>[\w-]+)/)?admin/users/reset/(?P<user_id>\d+)$', views_admin.users_reset, name='admin.users_reset'),
     url(r'^((?P<lang>[\w-]+)/)?admin/partida_list$', views_admin.partida_list, name='admin.partida_list'),
     url(r'^((?P<lang>[\w-]+)/)?admin/partida_detail/(?P<num_partida>\d+)/$', views_admin.partida_detail, name='admin.partida_detail'),


     url(r'^((?P<lang>[\w-]+)/)?ws/usuaris_registrats/', views_ws.usuaris_registrats, name='ws.usuaris_registrats'),
     url(r'^((?P<lang>[\w-]+)/)?ws/status_partida/', views_ws.status_partida, name='ws.status_partida'),
     url(r'^((?P<lang>[\w-]+)/)?ws/llistat_partides/', views_ws.llistat_partides, name='ws.llistat_partides'),
     url(r'^((?P<lang>[\w-]+)/)?ws/stats_partida/', views_ws.stats_partida, name='ws.stats_partida'),
     url(r'^((?P<lang>[\w-]+)/)?ws/tancar_ronda/(?P<num_partida>\d+)/', views_ws.tancar_ronda, name='ws.tancar_ronda'),
     url(r'^((?P<lang>[\w-]+)/)?ws/tancar_partida/(?P<num_partida>\d+)/', views_ws.tancar_partida, name='ws.tancar_partida'),
     url(r'^((?P<lang>[\w-]+)/)?ws/stats_partida_detail/(?P<num_partida>\d+)/', views_ws.stats_partida_detail, name='ws.stats_partida_detail'),
     url(r'^((?P<lang>[\w-]+)/)?ws/delete_user/(?P<id_user>\d+)/', views_ws.delete_user, name='ws.delete_user'),


     url(r'^((?P<lang>[\w-]+)/)?ws/demanar_dades/(?P<user_id>\d+)/', views_ws.demanar_dades, name='ws.demanar_dades'),
     url(r'^((?P<lang>[\w-]+)/)?ws/enviar_accio/(?P<user_id>\d+)/(?P<ronda_id>\d+)/(?P<result>[\w-]+)', views_ws.enviar_accio, name='ws.enviar_accio'),
     url(r'^((?P<lang>[\w-]+)/)?ws/demanar_resultat/(?P<user_id>\d+)/(?P<ronda_id>\d+)/', views_ws.demanar_resultat, name='ws.demanar_resultat'),


)
