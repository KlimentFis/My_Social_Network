from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from .models import MyUser
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from .models import Message
from django.db import transaction
from django.views.decorators.csrf import csrf_protect
from .models import Post, Post_Image
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import json

def login_or_register(request):
    return render(request, "user/log_or_reg.html")


def messages(request):
    all_users = set([request.user]) | set(request.user.friends.all()) | set(request.user.subscriptions.all()) | set(
        request.user.subscribers.all())
    for user in all_users:
        if user == request.user:
            user.username = "Избранное"

    return render(request, "user/messages.html", {
        "all_users": all_users,
        "current_user": None  # Добавляем значение по умолчанию
    })


@login_required
def chat_id(request, id):
    chat_user = get_object_or_404(MyUser, id=id)

    # Выбираем все сообщения между текущим пользователем и собеседником
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(recipient=chat_user)) |
        (Q(sender=chat_user) & Q(recipient=request.user))
    ).order_by('timestamp')  # Сортируем по времени

    # Обработка POST запроса для отправки нового сообщения
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            Message.objects.create(
                sender=request.user,
                recipient=chat_user,
                text=message_content
            )
        return HttpResponseRedirect(reverse('chat_id', args=[chat_user.id]))

    all_users = set([request.user]) | set(request.user.friends.all()) | set(request.user.subscriptions.all()) | set(
        request.user.subscribers.all())
    for i in all_users:
        if i.username == request.user.username:
            i.username = "Избранное"

    return render(request, "user/messages.html", {
        "messages": messages,
        "all_users": all_users,
        "current_user": chat_user
    })


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


@csrf_protect
@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        images = request.FILES.getlist('images')

        if not ((title and content) or images):
            return render(request, 'user/create_post.html', {
                'error': 'Please provide a title, content, or at least one image.'
            })

        try:
            with transaction.atomic():
                # Если title и content пустые, создаем пост с дефолтными значениями
                post = Post.objects.create(
                    title=title if title else "Untitled",
                    content=content if content else "Untitled",
                    author=request.user
                )

                # Если есть изображения, сохраняем их и привязываем к посту
                for image in images:
                    Post_Image.objects.create(image=image, post=post)
            # После успешного создания редиректим на страницу новостей
            return redirect('news')  # Здесь 'news' - это имя вашего маршрута, куда хотите направить

        except Exception as e:
            # Если произошла ошибка, возвращаем ошибку
            return render(request, 'user/create_post.html', {
                'error': f'Error while creating post: {e}'
            })

    return render(request, 'user/create_post.html')


@login_required
def delete_post(request):
    ...


@login_required
def user_logout(request):
    logout(request)
    return redirect('login_or_register')


@login_required
def upload_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')  # Безопасное получение файла
        if image_file:
            request.user.image = image_file
            request.user.save()
            return redirect("profile", id=request.user.id)  # Передаем id пользователя в URL
        else:
            # Обработка ошибки, если файл не предоставлен
            return redirect("profile", id=request.user.id)  # Можно указать сообщение об ошибке в сессии
    return redirect("profile", id=request.user.id)  # Перенаправление с id для корректного профиля



@login_required
def news(request):
    user = request.user

    # Получаем список друзей и подписок
    friends_and_subscriptions = MyUser.objects.filter(
        Q(pk__in=user.friends.all()) |  # ID друзей
        Q(pk__in=user.subscriptions.all())  # ID подписок
    )

    # Фильтруем посты только авторов из списка друзей и подписок
    posts = Post.objects.prefetch_related('images').filter(author__in=friends_and_subscriptions)

    return render(request, 'user/news.html', {'posts': posts})


@login_required
def profile(request, id):
    user = MyUser.objects.get(pk=id)
    posts = Post.objects.all().filter(author=id)
    return render(request, "user/profile.html", {"user": user, "posts": posts})


@csrf_protect
@login_required
def edit_profile(request):
    if request.method == "GET":
        return render(request, "user/edit_profile.html")
    elif request.method == "POST":
        request.user.bio = request.POST.get("BIO", "").strip()
        request.user.interests = request.POST.get("Interests", "").strip()
        request.user.country = request.POST.get("Country", "").strip()
        request.user.phone = request.POST.get("Phone", "").strip() or request.user.phone
        request.user.city = request.POST.get("City", "").strip() or request.user.city
        request.user.save()
        return redirect('profile', id=request.user.id)

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