# Generated by Django 5.1.1 on 2024-11-19 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_remove_post_images_remove_post_image_post_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post_image',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='user.post'),
        ),
    ]
