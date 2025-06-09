import requests
from django.core.management.base import BaseCommand
from main.models import Car
import random

class Command(BaseCommand):
    help = 'Populate the Car model with data from Car Query API'

    def handle(self, *args, **options):
        self.stdout.write('Fetching car makes...')
        makes_response = requests.get('https://www.carqueryapi.com/api/0.3/?cmd=getMakes')
        if makes_response.status_code != 200:
            self.stderr.write('Failed to fetch car makes')
            return

        makes_data = makes_response.json()
        makes = makes_data.get('Makes', [])
        if not makes:
            self.stderr.write('No makes found in API response')
            return

        total_cars_added = 0
        for make in makes:
            make_name = make.get('make_display')
            make_slug = make.get('make_slug')
            if not make_slug:
                continue

            self.stdout.write(f'Fetching models for make: {make_name}')
            models_response = requests.get(f'https://www.carqueryapi.com/api/0.3/?cmd=getModels&make={make_slug}')
            if models_response.status_code != 200:
                self.stderr.write(f'Failed to fetch models for make {make_name}')
                continue

            models_data = models_response.json()
            models = models_data.get('Models', [])
            for model in models:
                model_name = model.get('model_name')
                model_year = model.get('model_year')
                if not model_name or not model_year:
                    continue

                # Compose car name
                car_name = f"{make_name} {model_name}"

                # Check if car already exists
                if Car.objects.filter(name=car_name, year=model_year).exists():
                    continue

                # Create Car object with placeholder values for missing fields
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
                    self.stdout.write('Added 100 cars, stopping.')
                    return

        self.stdout.write(f'Total cars added: {total_cars_added}')
