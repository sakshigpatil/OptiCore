from django.contrib import admin
from .models import Holiday


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'is_recurring', 'country')
    list_filter = ('is_recurring', 'country')
    search_fields = ('name',)
