from django.urls import path

from api.views import ArticleView
from api.views import ArticleViewConcerts


app_name = "api"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('api/', ArticleView.as_view()),
    path('api_concerts/', ArticleViewConcerts.as_view()),
]

