# Generated by Django 3.2.5 on 2021-10-01 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_subcategory_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(default=321, max_length=150, unique=True),
            preserve_default=False,
        ),
    ]