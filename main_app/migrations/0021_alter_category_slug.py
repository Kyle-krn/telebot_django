# Generated by Django 3.2.5 on 2021-10-03 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0020_auto_20211004_0246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
