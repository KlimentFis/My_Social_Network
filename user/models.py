from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    image = models.ImageField(upload_to='users/', blank=True, null=True, verbose_name='Фото')
    friends = models.ManyToManyField(
        'self',
        blank=True,
        related_name='user_friends',
        symmetrical=True,  # Друзья имеют симметричные связи
        verbose_name='Друзья'
    )
    subscribers = models.ManyToManyField(
        'self',
        blank=True,
        related_name='user_subscribers',
        symmetrical=False,  # Подписчики - асимметричные отношения
        verbose_name='Подписчики'
    )
    subscriptions = models.ManyToManyField(
        'self',
        blank=True,
        related_name='user_subscriptions',
        symmetrical=False,   # Подписки также асимметричны
        verbose_name='Подписки'
    )

    phone = models.TextField('Телефон', blank=False)
    bio = models.TextField('Обо мне', blank=False)
    interests = models.TextField('Интересы', blank=False)
    country = models.TextField('Страна', blank=False)
    city = models.TextField('Город', blank=False)

    def __str__(self):
        return f"{self.first_name} {self.username}"

class Message(models.Model):
    sender = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='Отправитель')
    recipient = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='received_messages', verbose_name='Получатель')
    text = models.TextField(verbose_name='Сообщение')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время отправки')

    def __str__(self):
        return f"Сообщение от {self.sender} к {self.recipient} в {self.timestamp}"


# models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Post_Image(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)  # Загрузка изображений в папку media/post_images/

    def __str__(self):
        return f"Image for {self.post.title}"