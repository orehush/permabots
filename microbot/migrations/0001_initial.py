# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=100, verbose_name='Token', db_index=True)),
                ('enabled', models.BooleanField(default=True, verbose_name='Enable')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Date Modified')),
            ],
            options={
                'verbose_name': 'Bot',
                'verbose_name_plural': 'Bots',
            },
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('type', models.CharField(max_length=255, choices=[(b'private', 'Private'), (b'group', 'Group'), (b'supergroup', 'Supergroup'), (b'channel', 'Channel')])),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('username', models.CharField(max_length=255, null=True, blank=True)),
                ('first_name', models.CharField(max_length=255, null=True, blank=True)),
                ('last_name', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Chat',
                'verbose_name_plural': 'Chats',
            },
        ),
        migrations.CreateModel(
            name='Handler',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pattern', models.CharField(max_length=255, verbose_name='Pattern')),
                ('response_text_template', models.TextField(verbose_name='Text response template')),
                ('response_keyboard_template', models.TextField(null=True, verbose_name='Keyboard response template', blank=True)),
                ('enabled', models.BooleanField(default=True, verbose_name='Enable')),
                ('bot', models.ForeignKey(related_name='handlers', verbose_name='Bot', to='microbot.Bot')),
            ],
            options={
                'verbose_name': 'Handler',
                'verbose_name_plural': 'Handlers',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.BigIntegerField(serialize=False, verbose_name='Id', primary_key=True)),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('text', models.TextField(null=True, verbose_name='Text', blank=True)),
                ('chat', models.ForeignKey(related_name='messages', verbose_name='Chat', to='microbot.Chat')),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url_template', models.CharField(max_length=255, verbose_name='Url template')),
                ('method', models.CharField(default=b'Get', max_length=128, verbose_name='Method', choices=[(b'Get', 'Get'), (b'Post', 'Post'), (b'Put', 'Put'), (b'Delete', 'Delete')])),
                ('content_type', models.CharField(max_length=255, null=True, verbose_name='Content type', blank=True)),
                ('data', models.TextField(null=True, verbose_name='Data of the request', blank=True)),
            ],
            options={
                'verbose_name': 'Request',
                'verbose_name_plural': 'Requests',
            },
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('update_id', models.BigIntegerField(serialize=False, verbose_name='Id', primary_key=True)),
                ('message', models.ForeignKey(related_name='updates', verbose_name='Message', blank=True, to='microbot.Message', null=True)),
            ],
            options={
                'verbose_name': 'Update',
                'verbose_name_plural': 'Updates',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('first_name', models.CharField(max_length=255, verbose_name='First name')),
                ('last_name', models.CharField(max_length=255, null=True, verbose_name='Last name', blank=True)),
                ('username', models.CharField(max_length=255, null=True, verbose_name='User name', blank=True)),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.AddField(
            model_name='message',
            name='forward_from',
            field=models.ForeignKey(related_name='forwarded_from', verbose_name='Forward from', blank=True, to='microbot.User', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='from_user',
            field=models.ForeignKey(related_name='messages', verbose_name='User', to='microbot.User'),
        ),
        migrations.AddField(
            model_name='handler',
            name='request',
            field=models.OneToOneField(to='microbot.Request'),
        ),
        migrations.AddField(
            model_name='bot',
            name='user_api',
            field=models.OneToOneField(related_name='bot', null=True, blank=True, to='microbot.User', verbose_name='Bot User'),
        ),
    ]
