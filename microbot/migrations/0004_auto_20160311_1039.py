# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('microbot', '0003_auto_20160310_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='bot',
            name='owner',
            field=models.ForeignKey(related_name='bots', default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='headerparam',
            name='request',
            field=models.ForeignKey(related_name='header_parameters', verbose_name='Request', to='microbot.Request'),
        ),
        migrations.AlterField(
            model_name='urlparam',
            name='request',
            field=models.ForeignKey(related_name='url_parameters', verbose_name='Request', to='microbot.Request'),
        ),
    ]
