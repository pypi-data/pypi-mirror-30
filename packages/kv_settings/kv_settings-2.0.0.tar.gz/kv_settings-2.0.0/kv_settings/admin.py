from django.contrib import admin

from .models import (
    KeyValueSetting,
)


class KeyValueSettingAdmin(admin.ModelAdmin):
    search_fields = ('key', )
    list_display = ('key', 'added_on', 'updated_on')
    list_filter = ('added_on', )


admin.site.register(KeyValueSetting, KeyValueSettingAdmin)
