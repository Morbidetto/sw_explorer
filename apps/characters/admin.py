from django.contrib import admin

from characters.models import CharactersCsvFile

@admin.decorators.register(CharactersCsvFile)
class CharactersCsvFileAdmin(admin.ModelAdmin):
    list_display = ("id", "ctime", "mtime")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
