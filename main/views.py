from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Car, Review, Favorite, UserProfile
from .forms import ReviewForm, UserProfileForm

def index(request):
    car_of_the_week = Car.objects.order_by('-created_at').first()
    context = {
        'car_of_the_week': car_of_the_week
    }
    return render(request, 'main/index.html', context)

def cars(request):
    cars = Car.objects.all().order_by('-created_at')

    # Get filter parameters from request
    make = request.GET.get('make')
    model = request.GET.get('model')
    year = request.GET.get('year')
    vehicle_type = request.GET.get('vehicle_type')
    fuel_type = request.GET.get('fuel_type')
    transmission = request.GET.get('transmission')
    drive_wheel = request.GET.get('drive_wheel')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Filter queryset based on parameters
    if make:
        cars = cars.filter(make__icontains=make)
    if model:
        cars = cars.filter(model__icontains=model)
    if year:
        try:
            year_int = int(year)
            cars = cars.filter(year=year_int)
        except ValueError:
            pass
    if vehicle_type:
        cars = cars.filter(vehicle_type__iexact=vehicle_type)
    if fuel_type:
        cars = cars.filter(fuel_type__iexact=fuel_type)
    if transmission:
        cars = cars.filter(transmission__iexact=transmission)
    if drive_wheel:
        cars = cars.filter(drive_wheel=drive_wheel)
    if min_price:
        try:
            min_price_float = float(min_price)
            cars = cars.filter(price__gte=min_price_float)
        except ValueError:
            pass
    if max_price:
        try:
            max_price_float = float(max_price)
            cars = cars.filter(price__lte=max_price_float)
        except ValueError:
            pass

    # Get total count before pagination
    total_cars = cars.count()
    
    # Pagination
    paginator = Paginator(cars, 9)  # 9 cars per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'cars': page_obj,
        'total_cars': total_cars,
        'filter_make': make or '',
        'filter_model': model or '',
        'filter_year': year or '',
        'filter_vehicle_type': vehicle_type or '',
        'filter_fuel_type': fuel_type or '',
        'filter_transmission': transmission or '',
        'filter_drive_wheel': drive_wheel or '',
        'filter_min_price': min_price or '',
        'filter_max_price': max_price or '',
        'page_obj': page_obj,
    }

    return render(request, 'main/cars.html', context)

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    reviews = Review.objects.filter(car=car).order_by('-created_at')
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, car=car).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('main:login')
        if 'favorite_action' in request.POST:
            action = request.POST.get('favorite_action')
            if action == 'add':
                Favorite.objects.get_or_create(user=request.user, car=car)
            elif action == 'remove':
                Favorite.objects.filter(user=request.user, car=car).delete()
            return redirect('main:car_detail', car_id=car.id)
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.car = car
                review.user = request.user
                review.save()
                return redirect('main:car_detail', car_id=car.id)
    else:
        form = ReviewForm()

    context = {
        'car': car,
        'reviews': reviews,
        'form': form,
        'is_favorite': is_favorite,
    }
    return render(request, 'main/car_detail.html', context)

def about(request):
    return render(request, 'main/about.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('main:account')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'main/login.html'
    def get_success_url(self):
        return '/account'

@method_decorator(require_POST, name='dispatch')
class CustomLogoutView(View):
    def post(self, request, *args, **kwargs):
        auth_logout(request)
        return HttpResponseRedirect('/')

@login_required
def account(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('main:account')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'favorites': request.user.favorites.select_related('car').order_by('-created_at')
    }
    return render(request, 'main/account.html', context)
