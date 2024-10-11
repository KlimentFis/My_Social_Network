from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class MyUser(AbstractUser):
    image = models.ImageField(upload_to='users/', blank=True, null=True, verbose_name='Фото')
    friends = models.ManyToManyField('self', blank=True, related_name='user_friends', symmetrical=False, verbose_name='Друзья')

    def __str__(self):
        return f"{self.first_name} {self.username}"

class Message(models.Model):
    sender = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='Отправитель')
    recipient = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='received_messages', verbose_name='Получатель')
    text = models.TextField(verbose_name='Сообщение')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время отправки')

    def __str__(self):
        return f"Сообщение от {self.sender} к {self.recipient} в {self.timestamp}"
