from django.core.management.base import BaseCommand
from main.models import Car
from django.core.files.base import ContentFile
import random

class Command(BaseCommand):
    help = 'Creates sample car data'

    def handle(self, *args, **kwargs):
        # Sample car data
        cars_data = [
            {
                'name': '2023 Toyota Camry LE',
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2023,
                'color': 'Silver',
                'drive_wheel': 'fwd',
                'price': 25999.99,
                'description': 'Reliable and comfortable sedan with great fuel economy.'
            },
            {
                'name': '2022 Honda CR-V EX',
                'make': 'Honda',
                'model': 'CR-V',
                'year': 2022,
                'color': 'Blue',
                'drive_wheel': 'awd',
                'price': 28499.99,
                'description': 'Popular compact SUV with excellent safety features.'
            },
            {
                'name': '2023 Ford Mustang GT',
                'make': 'Ford',
                'model': 'Mustang',
                'year': 2023,
                'color': 'Red',
                'drive_wheel': 'rwd',
                'price': 45999.99,
                'description': 'Powerful sports car with iconic styling.'
            },
            {
                'name': '2022 BMW 330i',
                'make': 'BMW',
                'model': '3-Series',
                'year': 2022,
                'color': 'Black',
                'drive_wheel': 'rwd',
                'price': 42999.99,
                'description': 'Luxury sedan with dynamic performance.'
            },
            {
                'name': '2023 Tesla Model 3',
                'make': 'Tesla',
                'model': 'Model 3',
                'year': 2023,
                'color': 'White',
                'drive_wheel': 'awd',
                'price': 39999.99,
                'description': 'Electric sedan with cutting-edge technology.'
            },
            {
                'name': '2022 Jeep Wrangler Rubicon',
                'make': 'Jeep',
                'model': 'Wrangler',
                'year': 2022,
                'color': 'Green',
                'drive_wheel': '4wd',
                'price': 49999.99,
                'description': 'Capable off-road SUV with removable top.'
            },
            {
                'name': '2023 Mercedes-Benz C300',
                'make': 'Mercedes-Benz',
                'model': 'C-Class',
                'year': 2023,
                'color': 'Silver',
                'drive_wheel': 'rwd',
                'price': 47999.99,
                'description': 'Refined luxury sedan with premium features.'
            },
            {
                'name': '2022 Chevrolet Silverado 1500',
                'make': 'Chevrolet',
                'model': 'Silverado',
                'year': 2022,
                'color': 'Black',
                'drive_wheel': '4wd',
                'price': 52999.99,
                'description': 'Full-size pickup with impressive capability.'
            },
            {
                'name': '2023 Audi Q5',
                'make': 'Audi',
                'model': 'Q5',
                'year': 2023,
                'color': 'Blue',
                'drive_wheel': 'awd',
                'price': 44999.99,
                'description': 'Premium compact SUV with refined handling.'
            },
            {
                'name': '2022 Volkswagen Golf GTI',
                'make': 'Volkswagen',
                'model': 'Golf',
                'year': 2022,
                'color': 'Red',
                'drive_wheel': 'fwd',
                'price': 32999.99,
                'description': 'Hot hatchback with sporty performance.'
            }
        ]

        # Create cars
        for car_data in cars_data:
            car = Car.objects.create(**car_data)
            # Create a simple colored image as a placeholder
            img_data = f'<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg"><rect width="800" height="400" fill="{car_data["color"].lower()}"/><text x="400" y="200" font-family="Arial" font-size="40" fill="white" text-anchor="middle">{car_data["make"]} {car_data["model"]}</text></svg>'
            car.image.save(f'{car.id}.svg', ContentFile(img_data.encode()))
            self.stdout.write(f'Created car: {car.name}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample cars'))
