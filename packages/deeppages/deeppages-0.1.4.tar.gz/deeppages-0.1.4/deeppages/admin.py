from django.contrib import admin
from deeppages.models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    pass
