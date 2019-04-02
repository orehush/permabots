# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-04-02 07:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permabots', '0007_auto_20160530_0455'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to='')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='permabots.Message')),
            ],
            options={
                'verbose_name': 'Photo message',
                'verbose_name_plural': 'Photo messages',
            },
        ),
        migrations.AlterField(
            model_name='chat',
            name='type',
            field=models.CharField(choices=[('private', 'Private'), ('group', 'Group'), ('supergroup', 'Supergroup'), ('channel', 'Channel')], max_length=255),
        ),
        migrations.AlterField(
            model_name='hook',
            name='enabled',
            field=models.BooleanField(default=True, help_text='Enable/disable hook', verbose_name='Enable'),
        ),
        migrations.AlterField(
            model_name='messengermessage',
            name='type',
            field=models.CharField(choices=[('message', 'Message'), ('postback', 'Postback'), ('delivery', 'Delivery')], max_length=255),
        ),
        migrations.AlterField(
            model_name='request',
            name='method',
            field=models.CharField(choices=[('Get', 'Get'), ('Post', 'Post'), ('Put', 'Put'), ('Delete', 'Delete'), ('Patch', 'Patch')], default='Get', help_text='Define Http method for the request', max_length=128, verbose_name='Method'),
        ),
        migrations.AddField(
            model_name='message',
            name='photo',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                 null=True,
                                                                 verbose_name='Photo ids'),
        ),
        migrations.AlterField(
            model_name='message',
            name='forward_from',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='forwarded_from',
                                    to='permabots.User',
                                    verbose_name='Forward from'),
        ),
        migrations.AlterField(
            model_name='update',
            name='callback_query',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='updates',
                                    to='permabots.CallbackQuery',
                                    verbose_name='Callback Query'),
        ),
        migrations.AlterField(
            model_name='update',
            name='message',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='updates',
                                    to='permabots.Message',
                                    verbose_name='Message'),
        ),
    ]
