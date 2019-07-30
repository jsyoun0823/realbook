from django.db import models
from django.contrib.auth.models import User
import jsonfield
import json
import numpy as np

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    #array = jsonfield.JSONField()
    #likebooksindxs = jsonfield.JSONField()
    #lastrecs = jsonfield.JSONField()

    def __unicode__(self):
            return self.name

    def save(self, *args, **kwargs):
        create = kwargs.pop('create', None)
        print('create:',create)
        if create==True:
            super(UserProfile, self).save(*args, **kwargs)
"""
class BookRated(models.Model):
    user = models.ForeignKey(UserProfile, related_name='ratedbooks', on_delete=models.CASCADE)
    book = models.CharField(max_length=100)
    bookindx = models.IntegerField(default=1)
    value = models.IntegerField()

    def __unicode__(self):
        return self.book
"""

class BookData(models.Model):
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    author = models.CharField(max_length=100)
    info = models.TextField()
    keyword = models.TextField()

class ListBook(models.Model):
    user = models.ForeignKey(UserProfile, related_name='booklist', on_delete=models.CASCADE)
    book = models.CharField(max_length=100)

    def __unicode__(self):
        return self.book
