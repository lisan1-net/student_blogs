from django.contrib import admin
from django.apps import apps
from django.contrib.admin import ModelAdmin

ModelAdmin.list_per_page = 50

app = apps.get_app_config('main')
for model in app.get_models():
    admin.site.register(model)

admin.site.site_header = app.verbose_name
admin.site.site_title = app.verbose_name
