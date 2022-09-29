from django.db import models
from rest_framework import serializers


class StringListField(serializers.ListField):
    child = serializers.CharField()



# Create your models here.

# Create your models here.
class Matches(models.Model):
    Event = models.CharField(max_length=255, default = '')
    Date = models.DateTimeField(auto_now=False)
    Venue = models.CharField(max_length=255,default = '')
    Link =  models.CharField(max_length=255,default = '')
    img_url =  models.CharField(max_length=255,default = '')
    LikedArtists = StringListField()
    song_url =  StringListField()
    event_day =  models.CharField(max_length=255,default = '')
    day_mon_year =  models.CharField(max_length=255,default = '')
    event_day1 =  models.CharField(max_length=255,default = '')
    event_month =  models.CharField(max_length=255,default = '')
    event_year =  models.CharField(max_length=255,default = '')
    mon_year =  models.CharField(max_length=255,default = '')

    def __str__(self):
        return self.title


class Concerts(models.Model):
    Artist  = models.CharField(max_length=255, default = '')
    Date = models.CharField(max_length=255, default = '')
    Link = models.DateTimeField(auto_now=False)
    Venue = models.CharField(max_length=255,default = '')
    FiltArtist =  StringListField()
    img_url =  models.CharField(max_length=255,default = '')
    event_day =  models.CharField(max_length=255,default = '')
    day_mon_year =  models.CharField(max_length=255,default = '')
    event_day1 =  models.CharField(max_length=255,default = '')
    event_month =  models.CharField(max_length=255,default = '')
    event_year =  models.CharField(max_length=255,default = '')
    mon_year =  models.CharField(max_length=255,default = '')

    def __str__(self):
        return self.title


