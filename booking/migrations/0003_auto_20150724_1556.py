# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_auto_20150724_0930'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('booked', models.BooleanField(editable=False)),
                ('booked_for', models.CharField(max_length=50)),
                ('event', models.ForeignKey(to='booking.Event')),
            ],
        ),
        migrations.RemoveField(
            model_name='seat',
            name='booked',
        ),
        migrations.RemoveField(
            model_name='seat',
            name='booked_for',
        ),
        migrations.AddField(
            model_name='book',
            name='seat',
            field=models.ForeignKey(to='booking.Seat'),
        ),
    ]
