from django.contrib import admin

# Register your models here.

from .models import Concerts, Matches

admin.site.register(Matches)
admin.site.register(Concerts)

