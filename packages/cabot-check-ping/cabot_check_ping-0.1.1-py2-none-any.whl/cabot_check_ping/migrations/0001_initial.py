# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion

from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cabotapp', '0006_auto_20170821_1000'),
    ]

    operations = [
        migrations.CreateModel(
            name='PingStatusCheck',
            fields=[
                ('statuscheck_ptr',
                 models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='cabotapp.StatusCheck')),
                ('host',
                 models.TextField(
                    help_text=b'Host to check.')),
                ('packet_size',
                 models.PositiveIntegerField(
                    verbose_name=b'Packet size',
                    help_text=b'Packet size in data bytes.',
                    default=56)),
                ('count',
                 models.PositiveIntegerField(
                    help_text=b'Ping count.',
                    default=3)),
                ('max_rtt',
                 models.FloatField(
                    verbose_name=b'Max RTT',
                    help_text=b'Maximum RTT.',
                    validators=[MinValueValidator(0.0)],
                    default=70)),
            ],
            options={
                'abstract': False,
            },
            bases=('cabotapp.statuscheck',),
        ),
    ]
