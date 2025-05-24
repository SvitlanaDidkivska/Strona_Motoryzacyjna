from django.contrib import admin
from .models import Car

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'make', 'model', 'year', 'price', 'drive_wheel')
    list_filter = ('make', 'year', 'drive_wheel')
    search_fields = ('name', 'make', 'model')
    ordering = ('-created_at',)
