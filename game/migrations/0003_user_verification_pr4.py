# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20190515_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='verification_pr4',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
