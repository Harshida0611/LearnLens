from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def features(request):
    return render(request, "features.html")

def how_it_works(request):
    return render(request, "how_it_works.html")

def about(request):
    return render(request, "aboutus.html")

def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "registration.html")
