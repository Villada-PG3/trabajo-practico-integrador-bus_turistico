from django.shortcuts import render

def home(request):
    return render(request, 'public/home.html')

# Vistas temporales de prueba para evitar errores con los {% url %} del HTML
def recorridos_list(request):
    return render(request, 'public/home.html') # Temporal

def paradas_list(request):
    return render(request, 'public/home.html') # Temporal

def atractivos_list(request):
    return render(request, 'public/home.html') # Temporal

def admin_login(request):
    return render(request, 'public/home.html') # Temporal
