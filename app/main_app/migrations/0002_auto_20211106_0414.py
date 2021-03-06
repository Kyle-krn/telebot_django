# Generated by Django 3.2.8 on 2021-11-06 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='pk_for_telegram',
            field=models.CharField(blank=True, help_text='Используется в боте для поиска категории', max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='pk_for_telegram',
            field=models.CharField(blank=True, help_text='Используется в боте для поиска категории', max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='pk_for_telegram',
            field=models.CharField(blank=True, help_text='Используется в боте для поиска категории', max_length=255, null=True, unique=True),
        ),
    ]
