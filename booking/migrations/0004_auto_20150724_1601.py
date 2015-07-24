# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_auto_20150724_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='booked',
            field=models.BooleanField(editable=False, default=False),
        ),
    ]
