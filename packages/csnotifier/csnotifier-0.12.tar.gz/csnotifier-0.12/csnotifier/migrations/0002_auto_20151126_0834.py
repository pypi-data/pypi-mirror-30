# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csnotifier', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='pw_response',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='pw_status',
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='pw_status_message',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
