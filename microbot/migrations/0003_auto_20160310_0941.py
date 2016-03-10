# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microbot', '0002_environmentvar'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeaderParam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=255, verbose_name='Key')),
                ('value_template', models.CharField(max_length=255, verbose_name='Value template')),
                ('request', models.ForeignKey(related_name='header_parameters', verbose_name='Request', to='microbot.Bot')),
            ],
            options={
                'verbose_name': 'Header Parameter',
                'verbose_name_plural': 'Header Parameters',
            },
        ),
        migrations.CreateModel(
            name='UrlParam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=255, verbose_name='Key')),
                ('value_template', models.CharField(max_length=255, verbose_name='Value template')),
                ('request', models.ForeignKey(related_name='url_parameters', verbose_name='Request', to='microbot.Bot')),
            ],
            options={
                'verbose_name': 'Url Parameter',
                'verbose_name_plural': 'Url Parameters',
            },
        ),
        migrations.RemoveField(
            model_name='request',
            name='content_type',
        ),
    ]
