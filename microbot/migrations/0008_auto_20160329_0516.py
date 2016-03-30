# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-29 10:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('microbot', '0007_auto_20160328_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='microbot.Chat', verbose_name='Chat')),
            ],
            options={
                'verbose_name': 'Chats States',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='State name')),
                ('bot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='microbot.Bot', verbose_name='Bot')),
            ],
            options={
                'verbose_name': 'State',
                'verbose_name_plural': 'States',
            },
        ),
        migrations.AddField(
            model_name='chatstate',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat', to='microbot.State', verbose_name='State'),
        ),
        migrations.AddField(
            model_name='handler',
            name='source_states',
            field=models.ManyToManyField(related_name='source_handlers', to='microbot.State', verbose_name='Source States'),
        ),
        migrations.AddField(
            model_name='handler',
            name='target_state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='target_handlers', to='microbot.State', verbose_name='Target State'),
        ),
    ]