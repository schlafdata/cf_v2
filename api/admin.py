from django.contrib import admin

# Register your models here.

from .models import Concerts, Matches, Spotify

admin.site.register(Matches)
admin.site.register(Concerts)
admin.site.register(Spotify)


