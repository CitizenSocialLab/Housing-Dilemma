# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_user_verification_pr4'),
    ]

    operations = [
        migrations.AddField(
            model_name='partida',
            name='ronda_final',
            field=models.IntegerField(null=True),
        ),
    ]
