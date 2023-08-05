# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('uuid', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('token', models.CharField(max_length=250)),
                ('tags', models.TextField()),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('extra_context', models.TextField(null=True, blank=True)),
                ('tags', models.TextField(null=True, blank=True)),
                ('sent', models.BooleanField(default=False)),
                ('data', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
