from django.contrib import admin

from .models import *


class StorageEntryAdmin(admin.ModelAdmin):
    list_display = ('id','date_created','date_updated')

admin.site.register(Market)
admin.site.register(User)
admin.site.register(EntryType)
admin.site.register(Entries)
admin.site.register(StorageEntry,StorageEntryAdmin)
admin.site.register(StaticSettings)
admin.site.register(FAQ)
