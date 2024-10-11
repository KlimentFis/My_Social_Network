from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

from .models import MyUser
# Create your views here.
def login_or_register(request):
    return render(request, "user/log_or_reg.html")

def messages(request):
    return render(request, "user/messages.html")

@csrf_protect
def register(request):
    if request.method == "GET":
        return render(request, "user/register.html")
    else:
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        repeat_password = request.POST.get('repeat_password', '').strip()

        if password == repeat_password:
            # Создаем пользователя, но не передаем пароль напрямую
            user = MyUser(username=username, is_active=True, date_joined=timezone.now())

            # Хешируем пароль
            user.set_password(password)  # Используйте set_password для хеширования

            # Сохраняем пользователя
            user.save()

            # Логиним пользователя после регистрации
            login(request, user)

            # Перенаправляем на страницу новостей
            return redirect('news')
        return render(request, "user/register.html", {"error": "Passwords do not match"})


@csrf_protect
def user_login(request):
    if request.method == "GET":
        return render(request, "user/login.html")
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Аутентифицируем пользователя
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Успешная аутентификация
            login(request, user)
            return redirect("news")
        else:
            # Аутентификация не удалась — возвращаем ошибку
            return render(request, "user/login.html", {"error": "Invalid username or password"})

def create_post(request):
    if request.method == "GET":
        return render(request, "user/create_post.html")

def user_logout(request):
    logout(request)
    return redirect('login_or_register')

def news(request):
    return render(request, "user/news.html")

def profile(request):
    return render(request, "user/profile.html")

def friends(request):
    if request.method == "GET":
        return render(request, "user/user_list.html")
    else:
        ...
