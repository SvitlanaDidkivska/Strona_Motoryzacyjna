import requests
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from main.models import Car
import urllib.request
import json

class Command(BaseCommand):
    help = 'Fetch car data from NHTSA API'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, help='Year to fetch cars from')
        parser.add_argument('--limit', type=int, default=10, help='Number of cars to fetch')
        parser.add_argument('--offset', type=int, default=0, help='Offset for makes to start from')

    def get_car_image(self, make, model, year):
        """Fetch car image from manufacturer media sites."""
        try:
            # Clean up make and model names
            make_clean = make.lower().replace(' ', '-')
            model_clean = model.lower().replace(' ', '-')
            
            # Define brand-specific colors for the gradient
            brand_colors = {
                'FERRARI': '#FF2800',
                'LAMBORGHINI': '#DDB321',
                'PORSCHE': '#000000',
                'BMW': '#0066B1',
                'MERCEDES-BENZ': '#222222',
                'AUDI': '#BB0A30',
                'MASERATI': '#0C2340',
                'BENTLEY': '#4A2B1D',
                'ROLLS-ROYCE': '#311F1F',
                'BUGATTI': '#41007C'
            }

            color = brand_colors.get(make, '#333333')
            
            # Car silhouette path
            car_path = """M 100,280 C 120,280 130,280 150,280 L 200,280 C 220,280 240,260 280,260 
            L 520,260 C 560,260 580,280 600,280 L 650,280 C 670,280 680,280 700,280 L 700,290 
            C 680,290 670,300 650,300 L 600,300 C 580,300 560,320 520,320 L 280,320 C 240,320 
            220,300 200,300 L 150,300 C 130,300 120,290 100,290 Z"""
            
            svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
                        <stop offset="60%" style="stop-color:{color};stop-opacity:0.6" />
                        <stop offset="100%" style="stop-color:#000000;stop-opacity:1" />
                    </linearGradient>
                    <linearGradient id="shine" x1="-100%" y1="0%" x2="100%" y2="0%" gradientTransform="rotate(15)">
                        <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.1">
                            <animate attributeName="offset" values="-2;1" dur="3s" repeatCount="indefinite"/>
                        </stop>
                        <stop offset="50%" style="stop-color:#ffffff;stop-opacity:0.3">
                            <animate attributeName="offset" values="-1;2" dur="3s" repeatCount="indefinite"/>
                        </stop>
                        <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0.1">
                            <animate attributeName="offset" values="0;3" dur="3s" repeatCount="indefinite"/>
                        </stop>
                    </linearGradient>
                    <filter id="shadow">
                        <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
                    </filter>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                <rect width="100%" height="100%" fill="url(#grad)"/>
                <rect width="100%" height="400" fill="url(#shine)" opacity="0.5"/>
                
                <!-- Brand Logo Placeholder with Pulse Animation -->
                <circle cx="400" cy="100" r="40" fill="none" stroke="white" stroke-width="2" opacity="0.8">
                    <animate attributeName="r" values="40;42;40" dur="2s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>
                </circle>
                <text x="400" y="115" font-family="Arial" font-size="24" fill="white" text-anchor="middle" filter="url(#glow)">
                    {make[0]}
                    <animate attributeName="filter" values="url(#glow);url(#glow) brightness(1.2);url(#glow)" dur="2s" repeatCount="indefinite"/>
                </text>
                
                <!-- Car Details -->
                <text x="50%" y="35%" font-family="Arial" font-size="32" fill="white" text-anchor="middle" filter="url(#shadow)">{year} {make}</text>
                <text x="50%" y="45%" font-family="Arial" font-size="28" fill="white" text-anchor="middle" filter="url(#shadow)">{model}</text>
                
                <!-- Enhanced Car Silhouette -->
                <g transform="translate(0,20)">
                    <!-- Main Body -->
                    <path d="{car_path}" stroke="white" stroke-width="2" fill="none" filter="url(#shadow)"/>
                    
                    <!-- Wheels -->
                    <circle cx="200" cy="290" r="30" stroke="white" stroke-width="2" fill="none"/>
                    <circle cx="600" cy="290" r="30" stroke="white" stroke-width="2" fill="none"/>
                    <circle cx="200" cy="290" r="20" stroke="white" stroke-width="1" fill="none"/>
                    <circle cx="600" cy="290" r="20" stroke="white" stroke-width="1" fill="none"/>
                    
                    <!-- Windows -->
                    <path d="M300,260 L380,220 L520,220 L580,260" stroke="white" stroke-width="1" fill="none" opacity="0.6"/>
                    
                    <!-- Headlights -->
                    <path d="M120,270 L140,270 L140,280 L120,280 Z" stroke="white" stroke-width="1" fill="white" opacity="0.6"/>
                    <path d="M660,270 L680,270 L680,280 L660,280 Z" stroke="white" stroke-width="1" fill="white" opacity="0.6"/>
                </g>
            </svg>'''
            
            self.stdout.write(self.style.WARNING(
                f'Using placeholder image for {year} {make} {model}'
            ))
            return ContentFile(svg.encode(), name=f"{make}_{model}_{year}.svg")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch image: {str(e)}'))
        return None

    def handle(self, *args, **options):
        year = options['year'] or 2023
        limit = options['limit']
        
        self.stdout.write(f'Fetching car data for year {year}...')
        
        # Use specific popular makes that are likely to have images
        popular_makes = [
            {'MakeId': 1, 'MakeName': 'FERRARI'},
            {'MakeId': 2, 'MakeName': 'LAMBORGHINI'},
            {'MakeId': 3, 'MakeName': 'MASERATI'},
            {'MakeId': 4, 'MakeName': 'BENTLEY'},
            {'MakeId': 5, 'MakeName': 'ROLLS-ROYCE'},
            {'MakeId': 6, 'MakeName': 'BUGATTI'},
            {'MakeId': 7, 'MakeName': 'MCLAREN'},
            {'MakeId': 8, 'MakeName': 'ASTON MARTIN'},
            {'MakeId': 9, 'MakeName': 'PORSCHE'},
            {'MakeId': 10, 'MakeName': 'BMW M'},
            {'MakeId': 11, 'MakeName': 'MERCEDES-AMG'},
            {'MakeId': 12, 'MakeName': 'AUDI RS'},
            {'MakeId': 13, 'MakeName': 'LEXUS F'},
            {'MakeId': 14, 'MakeName': 'JAGUAR'},
            {'MakeId': 15, 'MakeName': 'LOTUS'}
        ]
        # Get list of makes we already have in the database
        existing_makes = set(Car.objects.values_list('make', flat=True).distinct())
        # Filter out makes we already have
        new_makes = [make for make in popular_makes if make['MakeName'] not in existing_makes]
        makes = new_makes[:limit]
        processed_count = 0
        
        for make in makes:
            if processed_count >= limit:
                break
                
            make_name = make.get('MakeName')
            if not make_name:
                continue
            
            # Fetch models for this make
            models_url = f'https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/{make_name}?format=json'
            models_response = requests.get(models_url)
            models_data = models_response.json()
            
            if 'Results' not in models_data:
                continue
            
            for model in models_data['Results']:
                if processed_count >= limit:
                    break
                    
                model_name = model.get('Model_Name')
                if not model_name:
                    continue
                
                # Get detailed vehicle info
                details_url = f'https://vpic.nhtsa.dot.gov/api/vehicles/GetVehicleTypesForMakeId/{make["MakeId"]}?format=json'
                details_response = requests.get(details_url)
                details_data = details_response.json()
                
                vehicle_type = 'Car'
                if 'Results' in details_data and details_data['Results']:
                    vehicle_type = details_data['Results'][0].get('VehicleTypeName', 'Car')
                
                # Generate some random data for fields not provided by the API
                colors = ['Black', 'White', 'Silver', 'Red', 'Blue', 'Gray']
                drive_wheels = ['fwd', 'rwd', '4wd', 'awd']
                fuel_types = ['Gasoline', 'Diesel', 'Electric', 'Hybrid']
                transmissions = ['Automatic', 'Manual', 'CVT']
                
                # Try to get an image for the car
                image_file = self.get_car_image(make_name, model_name, year)
                
                # Create or update the car
                car, created = Car.objects.get_or_create(
                    make=make_name,
                    model=model_name,
                    year=year,
                    defaults={
                        'name': f'{year} {make_name} {model_name}',
                        'price': Decimal(random.randint(20000, 80000)),
                        'color': random.choice(colors),
                        'drive_wheel': random.choice(drive_wheels),
                        'description': f'A {year} {make_name} {model_name} with modern features and reliable performance.',
                        'vehicle_type': vehicle_type,
                        'fuel_type': random.choice(fuel_types),
                        'engine': f'{random.randint(15, 60)/10}L {random.randint(3, 8)}-cylinder',
                        'transmission': random.choice(transmissions),
                        'doors': random.choice([2, 4, 5]),
                        'seats': random.choice([2, 4, 5, 7, 8]),
                        'manufacturer_code': f'{make_name[:3]}{year}',
                        'plant_country': 'United States',
                        'safety_rating': Decimal(random.randint(30, 50))/10
                    }
                )

                if image_file:
                    car.image.save(f"{make_name}_{model_name}_{year}.jpg", image_file, save=True)
                
                action = 'Created' if created else 'Updated'
                self.stdout.write(self.style.SUCCESS(
                    f'{action} {year} {make_name} {model_name}'
                ))
                
                processed_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed {processed_count} cars'
        ))
