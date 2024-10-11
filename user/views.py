from django.contrib.auth import login, logout, get_user_model, authenticate
# from django.utils import timezone
from django.shortcuts import render, redirect
from .models import MyUser
# Create your views here.
def login_or_register(request):
    return render(request, "user/log_or_reg.html")

def messages(request):
    return render(request, "user/messages.html")

def register(request):
    if request.method == "GET":
        return render(request, "user/register.html")
    else:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        repeate_password = request.POST.get('repeate_password', '')

        if password == repeate_password:
            user = MyUser.objects.create(username=username, password=password)
            # user = MyUser.objects.create(username=username, password=password, data_joined=timezone.now())
            # user.date_joined = timezone.now()  # Установка даты присоединения
            user.save()

            User = get_user_model()
            user = User.objects.filter(username=username).first()

            context = {
                'error': '',
            }

            login(request, user)
            # logout(request, user)
        return render(request, "user/news.html")

def login(request):
    if request.method == "GET":
        return render(request, "user/login.html")
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Редиректим на другую страницу, если необходимо
            return redirect('news')
        return render(request, "user/login.html")

def user_logout(request):
    logout(request)
    return redirect('login_or_register')

def news(request):
    return redirect(request, "user/news.html")

def profile(request):
    return render(request, "user/profile.html")