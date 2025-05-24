from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseRedirect
from .models import Car
from .views_account import account

def index(request):
    car_of_the_week = Car.objects.order_by('-created_at').first()
    context = {
        'car_of_the_week': car_of_the_week
    }
    return render(request, 'main/index.html', context)


def cars(request):
    cars = Car.objects.all().order_by('-created_at')

    make = request.GET.get('make')
    model = request.GET.get('model')
    year = request.GET.get('year')
    color = request.GET.get('color')
    drive_wheel = request.GET.get('drive_wheel')

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
    if color:
        cars = cars.filter(color__icontains=color)
    if drive_wheel:
        cars = cars.filter(drive_wheel=drive_wheel)

    context = {
        'cars': cars,
        'filter_make': make or '',
        'filter_model': model or '',
        'filter_year': year or '',
        'filter_color': color or '',
        'filter_drive_wheel': drive_wheel or '',
    }

    return render(request, 'main/cars.html', context)

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
