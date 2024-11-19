# Generated by Django 5.1.1 on 2024-11-19 18:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_post_image_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='images',
        ),
        migrations.RemoveField(
            model_name='post_image',
            name='post_id',
        ),
        migrations.AddField(
            model_name='post_image',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='user.post'),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='post_image',
            name='image',
            field=models.ImageField(upload_to='post_images/'),
        ),
    ]
