from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        repeat_password = request.POST.get('repeat_password', '')

        # Проверяем, существует ли уже пользователь с таким именем
        if MyUser.objects.filter(username=username).exists():
            return render(request, "user/register.html", {"error": "Username already taken"})

        if password == repeat_password:
            # Создаем пользователя с необходимыми полями
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

@login_required
def friends(request):
    if request.method == "GET":
        # Получаем списки друзей, подписчиков и подписок
        friends = request.user.friends.all()
        subscribers = request.user.subscribers.all()
        subscriptions = request.user.subscriptions.all()

        # Объединяем всех пользователей из этих категорий
        related_users = friends | subscribers | subscriptions

        # Получаем остальных пользователей, исключая тех, кто в связанных списках
        other_users = MyUser.objects.exclude(id__in=related_users.values_list('id', flat=True)).exclude(
            username=request.user.username)

        # Формируем контекст
        context = {
            "friends": friends,
            "subscribers": subscribers,
            "subscriptions": subscriptions,
            "other_users": other_users,
        }
        return render(request, "user/user_list.html", context)

    elif request.method == "POST":
        user_id = request.POST.get('user_id')

        try:
            target_user = MyUser.objects.get(id=user_id)
        except MyUser.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)

        action = request.POST.get('action')

        if action == 'add_friend':
            request.user.subscriptions.add(target_user)
            target_user.subscribers.add(request.user)
            return JsonResponse({"status": "success"})

        elif action == 'remove_friend':
            request.user.friends.remove(target_user)
            target_user.subscribers.remove(request.user)
            return JsonResponse({"status": "success"})

        elif action == 'unfollow_user':
            request.user.subscriptions.remove(target_user)
            return JsonResponse({"status": "success"})

        return JsonResponse({"status": "error", "message": "Invalid action"}, status=400)