# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnvironmentVar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=255, verbose_name='Key')),
                ('value', models.CharField(max_length=255, verbose_name='Value')),
                ('bot', models.ForeignKey(related_name='env_vars', verbose_name='Bot', to='microbot.Bot')),
            ],
            options={
                'verbose_name': 'Environment Var',
                'verbose_name_plural': 'Environment Vars',
            },
        ),
    ]
