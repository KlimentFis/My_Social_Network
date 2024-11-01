from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
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


def profile(request):
    return render(request, "user/profile.html")


from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


# class FriendsView(View):
#     def get(self, request):
#         # Получаем текущего пользователя
#         current_user = request.user
#
#         # Получаем пользователей в каждой из категорий
#         friends = current_user.friends.all()  # Предполагается, что есть связь ManyToMany с друзьями
#         subscribers = current_user.subscribers.all()
#         subscriptions = current_user.subscriptions.all()
#
#         # Объединяем всех пользователей, которых нужно исключить
#         excluded_users = list(friends) + list(subscribers) + list(subscriptions)
#
#         # Получаем других пользователей, исключая тех, кто уже в friends, subscribers или subscriptions
#         other_users = MyUser.objects.exclude(id=current_user.id)\
#             .exclude(id__in=[user.id for user in excluded_users])
#
#         # Передаем данные в шаблон
#         context = {
#             'friends': friends,
#             'subscribers': subscribers,
#             'subscriptions': subscriptions,
#             'other_users': other_users,
#         }
#
#         return render(request, 'friends.html', context)  # Убедитесь, что ваш шаблон называется 'friends.html'

@login_required
def friends(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get('user_id')
        action = data.get('action')

        target_user = MyUser.objects.get(id=user_id)

        if action == 'add_friend':
            # Если target_user уже подписан на текущего пользователя
            if target_user in request.user.subscribers.all():
                # Делаем их друзьями
                request.user.friends.add(target_user)
                target_user.friends.add(request.user)

                # Удаляем их из подписчиков и подписок
                request.user.subscriptions.remove(target_user)
                target_user.subscribers.remove(request.user)
            else:
                # Если не подписан, просто добавляем в подписки
                request.user.subscriptions.add(target_user)
                target_user.subscribers.add(request.user)

                # Теперь, когда текущий пользователь подписывается на target_user,
                # делаем их друзьями и удаляем из подписчиков
                request.user.friends.add(target_user)
                target_user.friends.add(request.user)
                request.user.subscribers.remove(target_user)
                target_user.subscribers.remove(request.user)

            return JsonResponse({"status": "success"})  # Успешный ответ

        elif action == 'remove_friend':
            # Удаляем из друзей
            request.user.friends.remove(target_user)
            target_user.friends.remove(request.user)

            # После удаления из друзей добавляем их обратно в подписчики
            request.user.subscribers.add(target_user)
            target_user.subscribers.add(request.user)

            return JsonResponse({"status": "success"})  # Успешный ответ

        elif action == 'unfollow_user':
            # Удаляем из подписок
            request.user.subscriptions.remove(target_user)
            target_user.subscribers.remove(request.user)

            return JsonResponse({"status": "success"})  # Успешный ответ

    # Получаем все списки
    friends = request.user.friends.all()

    # Получаем подписчиков, исключая друзей
    subscribers = request.user.subscribers.exclude(id__in=friends.values_list('id', flat=True))

    # Получаем подписки, исключая друзей
    subscriptions = request.user.subscriptions.exclude(id__in=friends.values_list('id', flat=True))

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