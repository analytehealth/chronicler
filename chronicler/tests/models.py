''' Test models for running the chronicler test suite '''
from django.db import models


class Person(models.Model):

    name = models.CharField(max_length=12)


class Group(models.Model):

    name = models.CharField(max_length=12)
    people = models.ManyToManyField('Person', through='Membership')


class Membership(models.Model):

    person = models.ForeignKey('Person')
    group = models.ForeignKey('Group')
    gold_member = models.BooleanField(default=False)
