# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='enquesta_final_pr10',
        ),
        migrations.RemoveField(
            model_name='user',
            name='enquesta_final_pr11',
        ),
        migrations.RemoveField(
            model_name='user',
            name='enquesta_final_pr7',
        ),
        migrations.RemoveField(
            model_name='user',
            name='enquesta_final_pr8',
        ),
        migrations.RemoveField(
            model_name='user',
            name='enquesta_final_pr9',
        ),
    ]
