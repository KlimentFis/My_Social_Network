from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from .models import MyUser
import json

# Create your views here.
def login_or_register(request):
    return render(request, "user/log_or_reg.html")


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Message
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


def messages(request):
    # Получаем всех друзей пользователя
    all_users = set([request.user]) | set(request.user.friends.all()) | set(request.user.subscriptions.all()) | set(
        request.user.subscribers.all())
    for user in all_users:
        if user == request.user:
            user.username = "Избранное"

    return render(request, "user/messages.html", {"friends": all_users})


def chat_id(request, pk):
    messages = Message.objects.filter(recipient = pk) | Message.objects.filter(sender = pk)
    return render(request, "user/message.html", {"messages": messages})

@csrf_exempt
def send_message(request, user_id):
    if request.method == "POST":
        # Получаем отправленное сообщение
        message_text = request.POST.get('message')
        friend = get_object_or_404(User, pk=user_id)

        # Создаем и сохраняем новое сообщение
        message = Message.objects.create(
            sender=request.user,
            receiver=friend,
            text=message_text
        )

        return JsonResponse({"success": True}, status=200)


@csrf_protect
def user_register(request):
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


def profile(request, id):
    user = MyUser.objects.get(pk=id)
    print(user.username)
    return render(request, "user/profile.html", {"user": user})


def edit_profile(request):
    if request.method == "GET":
        return render(request, "user/edit_profile.html")
    elif request.method == "POST":
        request.user.bio = request.POST.get("BIO", "").strip()
        request.user.interests = request.POST.get("Interests", "").strip()
        request.user.phone = request.POST.get("Phone", "").strip()
        request.user.country = request.POST.get("Country", "").strip()
        request.user.city = request.POST.get("City", "").strip()
        request.user.save()
        return redirect("profile")


@login_required
def friends(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get('user_id')
        action = data.get('action')

        try:
            target_user = MyUser.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return JsonResponse({"status": "error", "message": "User not found"}, status=404)

        if action == 'add_friend':
            if target_user in request.user.subscribers.all():
                # Если пользователь подписан на нас, добавляем его в друзья
                request.user.friends.add(target_user)
                target_user.friends.add(request.user)

                # Удаляем друг друга из подписчиков и подписок
                request.user.subscriptions.remove(target_user)
                target_user.subscribers.remove(request.user)
            else:
                # Если нет взаимной подписки, добавляем его в подписки
                request.user.subscriptions.add(target_user)
                target_user.subscribers.add(request.user)

            return JsonResponse({"status": "success"})

        elif action == 'remove_friend':
            # Удаляем из друзей
            request.user.friends.remove(target_user)
            target_user.friends.remove(request.user)

            # Добавляем обратно в подписчики
            request.user.subscribers.add(target_user)
            target_user.subscribers.add(request.user)

            # Добавляем в подписки
            request.user.subscriptions.add(target_user)
            target_user.subscriptions.add(request.user)

            return JsonResponse({"status": "success"})

        elif action == 'unfollow_user':
            # Удаляем из подписок
            request.user.subscriptions.remove(target_user)
            target_user.subscribers.remove(request.user)

            return JsonResponse({"status": "success"})

    # Получаем всех друзей пользователя
    friends = request.user.friends.all()

    # Получаем подписчиков, которые не являются друзьями
    subscribers = request.user.subscribers.exclude(id__in=friends.values_list('id', flat=True))

    # Получаем подписки, которые не являются друзьями
    subscriptions = request.user.subscriptions.exclude(id__in=friends.values_list('id', flat=True))

    # Исключаем друзей, подписчиков и подписки из общего списка пользователей
    excluded_user_ids = list(friends.values_list('id', flat=True)) + \
                        list(subscribers.values_list('id', flat=True)) + \
                        list(subscriptions.values_list('id', flat=True))

    other_users = MyUser.objects.exclude(id__in=excluded_user_ids).exclude(id=request.user.id)

    context = {
        'friends': friends,
        'subscribers': subscribers,
        'subscriptions': subscriptions,
        'other_users': other_users,
    }

    return render(request, 'user/user_list.html', context)