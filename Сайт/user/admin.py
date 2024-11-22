from django.contrib import admin
from user.models import MyUser, Message, Post, Post_Image

# Register your models here.
admin.site.register(MyUser)
admin.site.register(Message)
admin.site.register(Post)
admin.site.register(Post_Image)