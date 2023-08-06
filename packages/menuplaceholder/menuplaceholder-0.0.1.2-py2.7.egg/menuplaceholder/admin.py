from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from .models import MenuPlaceholder

admin.site.register(MenuPlaceholder, PageAdmin)
