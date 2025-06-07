from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Car
import requests
import random

class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'make', 'model', 'year', 'price', 'drive_wheel')
    list_filter = ('make', 'year', 'drive_wheel')
    search_fields = ('name', 'make', 'model')
    ordering = ('-created_at',)

    change_list_template = "admin/main/car_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate-cars/', self.admin_site.admin_view(self.populate_cars), name='populate-cars'),
        ]
        return custom_urls + urls

    def populate_cars(self, request):
        self.message_user(request, "Starting to populate cars from API...", level=messages.INFO)
        makes_response = requests.get('https://www.carqueryapi.com/api/0.3/?cmd=getMakes')
        if makes_response.status_code != 200:
            self.message_user(request, "Failed to fetch car makes from API.", level=messages.ERROR)
            return redirect('..')

        makes_data = makes_response.json()
        makes = makes_data.get('Makes', [])
        if not makes:
            self.message_user(request, "No makes found in API response.", level=messages.ERROR)
            return redirect('..')

        total_cars_added = 0
        for make in makes:
            make_name = make.get('make_display')
            make_slug = make.get('make_slug')
            if not make_slug:
                continue

            models_response = requests.get(f'https://www.carqueryapi.com/api/0.3/?cmd=getModels&make={make_slug}')
            if models_response.status_code != 200:
                continue

            models_data = models_response.json()
            models = models_data.get('Models', [])
            for model in models:
                model_name = model.get('model_name')
                model_year = model.get('model_year')
                if not model_name or not model_year:
                    continue

                car_name = f"{make_name} {model_name}"

                if Car.objects.filter(name=car_name, year=model_year).exists():
                    continue

                car = Car(
                    name=car_name,
                    make=make_name,
                    model=model_name,
                    year=int(model_year),
                    price=round(random.uniform(5000, 50000), 2),
                    color=random.choice(['Red', 'Blue', 'Black', 'White', 'Silver', 'Green']),
                    drive_wheel=random.choice(['fwd', 'rwd', '4wd', 'awd']),
                    description=f"{car_name} from year {model_year}.",
                )
                car.save()
                total_cars_added += 1

                if total_cars_added >= 100:
                    self.message_user(request, f'Added 100 cars, stopping.', level=messages.SUCCESS)
                    return redirect('..')

        self.message_user(request, f'Total cars added: {total_cars_added}', level=messages.SUCCESS)
        return redirect('..')

admin.site.register(Car, CarAdmin)
