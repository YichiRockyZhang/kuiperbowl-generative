# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-11-18 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_auto_20181118_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(max_length=200),
        ),
        migrations.AlterField(
            model_name='room',
            name='buzz_end_time',
            field=models.FloatField(default=1542553952.662831),
        ),
        migrations.AlterField(
            model_name='room',
            name='buzz_start_time',
            field=models.FloatField(default=1542553951.662831),
        ),
        migrations.AlterField(
            model_name='room',
            name='end_time',
            field=models.FloatField(default=1542553952.662831),
        ),
        migrations.AlterField(
            model_name='room',
            name='start_time',
            field=models.FloatField(default=1542553951.662831),
        ),
    ]