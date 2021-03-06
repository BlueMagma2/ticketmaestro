# -*- coding: utf-8 -*-
from django.db import models


class Venue(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(models.Model):
    venue = models.ForeignKey(Venue)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Section(models.Model):
    venue = models.ForeignKey(Venue)
    label = models.CharField(max_length=20)
    rank = models.IntegerField()

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return self.label


class Row(models.Model):
    section = models.ForeignKey(Section)
    label = models.CharField(max_length=20)
    rank = models.IntegerField()

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return self.label


class Seat(models.Model):
    row = models.ForeignKey(Row)
    number = models.IntegerField()

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return self.number

class Book(models.Model):
    event = models.ForeignKey(Event)
    seat = models.ForeignKey(Seat)
    booked = models.BooleanField(editable=False, default=False)
    booked_for = models.CharField(max_length=50, default="")
