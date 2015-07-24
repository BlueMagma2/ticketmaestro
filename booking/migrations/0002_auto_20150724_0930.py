# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='event',
        ),
        migrations.AddField(
            model_name='section',
            name='venue',
            field=models.ForeignKey(to='booking.Venue', default=1),
            preserve_default=False,
        ),
    ]
