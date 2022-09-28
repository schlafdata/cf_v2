from rest_framework import serializers
from .models import Matches
from .models import Concerts

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matches
        fields = ('Event','Date','Venue','Link','img_url','LikedArtists','song_url')


class ArticleSerializerConcerts(serializers.ModelSerializer):
    class Meta:
        model = Concerts
        fields = ('Artist','Date','Link','Venue','FiltArtist','img_url')

