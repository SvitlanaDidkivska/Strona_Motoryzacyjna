from django import template
from django.utils.safestring import mark_safe
import hashlib

register = template.Library()

@register.filter
def unique(queryset, field):
    """Return unique values from queryset based on field."""
    if hasattr(queryset, 'values_list'):
        values = list(queryset.values_list(field, flat=True).distinct())
        # Filter out None and empty values
        values = [v for v in values if v]
        
        # Normalize values to handle case sensitivity and whitespace
        normalized_values = []
        seen = set()
        
        for value in values:
            if isinstance(value, str):
                # Normalize string values
                norm_value = value.strip().title()
                if norm_value not in seen:
                    seen.add(norm_value)
                    normalized_values.append(value)
            else:
                # Handle non-string values (like years)
                if value not in seen:
                    seen.add(value)
                    normalized_values.append(value)
        
        # Handle special case for year field
        if field == 'year':
            return sorted(normalized_values, reverse=True)
        return sorted(normalized_values)
    return []

@register.filter
def car_placeholder(car):
    """Generate a placeholder image for cars without images."""
    # Generate a color based on the car's make
    color_hash = hashlib.md5(car.make.encode()).hexdigest()[:6]
    
    svg = f'''
    <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#{color_hash};stop-opacity:0.2" />
                <stop offset="100%" style="stop-color:#1a202c;stop-opacity:0.1" />
            </linearGradient>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                <feOffset dx="2" dy="2"/>
                <feComponentTransfer>
                    <feFuncA type="linear" slope="0.3"/>
                </feComponentTransfer>
                <feMerge>
                    <feMergeNode/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="#1a202c"/>
        <rect width="100%" height="100%" fill="url(#grad)"/>
        
        <!-- Car silhouette -->
        <g transform="translate(100,120) scale(0.8)" filter="url(#shadow)">
            <path d="M10,80 C10,80 60,80 80,80 C100,80 110,60 130,60 C160,60 180,80 200,80 
                     C220,80 240,60 260,60 C280,60 290,80 310,80 C330,80 380,80 380,80 L380,120 L10,120 Z" 
                  fill="none" stroke="#{color_hash}" stroke-width="2"/>
            <circle cx="100" cy="120" r="20" fill="none" stroke="#{color_hash}" stroke-width="2"/>
            <circle cx="300" cy="120" r="20" fill="none" stroke="#{color_hash}" stroke-width="2"/>
        </g>
        
        <!-- Text content -->
        <text x="50%" y="42%" font-family="Arial" font-size="24" fill="white" text-anchor="middle" font-weight="bold" filter="url(#shadow)">
            {car.make}
        </text>
        <text x="50%" y="58%" font-family="Arial" font-size="20" fill="#718096" text-anchor="middle">
            {car.model}
        </text>
        <text x="50%" y="70%" font-family="Arial" font-size="16" fill="#4a5568" text-anchor="middle">
            {car.year} • {car.vehicle_type or 'Vehicle'}
        </text>
        
        <!-- Additional details -->
        <text x="50%" y="82%" font-family="Arial" font-size="14" fill="#4a5568" text-anchor="middle">
            {car.transmission or ''} {car.fuel_type or ''}
        </text>
    </svg>
    '''
    
    return mark_safe(f"data:image/svg+xml;base64,{svg.encode('utf-8').hex()}")

@register.filter
def get_drive_wheel_icon(drive_wheel):
    """Return Font Awesome icon class for drive wheel type."""
    icons = {
        'fwd': 'fa-arrow-up',
        'rwd': 'fa-arrow-down',
        '4wd': 'fa-arrows-up-down',
        'awd': 'fa-arrows'
    }
    return icons.get(drive_wheel, 'fa-question')

@register.filter
def get_fuel_type_icon(fuel_type):
    """Return Font Awesome icon class for fuel type."""
    icons = {
        'Gasoline': 'fa-gas-pump',
        'Diesel': 'fa-truck-monster',
        'Electric': 'fa-bolt',
        'Hybrid': 'fa-leaf',
    }
    return icons.get(fuel_type, 'fa-question')

@register.filter
def get_transmission_icon(transmission):
    """Return Font Awesome icon class for transmission type."""
    icons = {
        'Automatic': 'fa-a',
        'Manual': 'fa-m',
        'CVT': 'fa-c',
    }
    return icons.get(transmission, 'fa-gear')
