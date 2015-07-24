# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_auto_20150724_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='booked_for',
            field=models.CharField(default='', max_length=50),
        ),
    ]
