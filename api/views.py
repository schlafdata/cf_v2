# Create your views here.
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from api.scripts import cf_main

from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ArticleSerializer, ArticleSerializerConcerts


def runScript(username):
    # try:
    import time
    start_time = time.time()

    result = cf_main.findMatches(username, 'soundcloud')
    matches = result[0]
    return matches

class ArticleView(APIView):
    def get(self, request):
        # articles = Article.objects.all()

        user = str(request.GET['username']).rstrip('/')
        data = runScript(user)
        # the many param informs the serializer that it will be serializing more than a single article.
        serializer = ArticleSerializer(data, many=True)
        resp = serializer.data
        return Response(resp)


def runScriptConcerts(user, date):
    # try:
    import time
    start_time = time.time()

    result = cf_main.get_raw_concerts(user, date)
    concerts = result[0]

    return concerts


class ArticleViewConcerts(APIView):
    def get(self, request):
        user = str(request.GET['venue']).rstrip('/')
        date = '  '.join(str(request.GET['month']).rstrip('/').split('-'))
        data = runScriptConcerts(user,date)
        # the many param informs the serializer that it will be serializing more than a single article.
        serializer = ArticleSerializerConcerts(data, many=True)
        resp = serializer.data
        return Response(resp)




def runScriptSpotify(username):
    # try:
    import time
    start_time = time.time()

    result = cf_main.findMatches(username, 'spotify')
    matches = result[0]
    return matches

class ArticleViewSpotify(APIView):
    def get(self, request):
        # articles = Article.objects.all()

        user = str(request.GET['bearer']).rstrip('/')
        data = runScriptSpotify(user)
        # the many param informs the serializer that it will be serializing more than a single article.
        serializer = ArticleSerializer(data, many=True)

        resp = serializer.data
        return Response(resp)


