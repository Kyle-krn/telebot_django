# Generated by Django 3.2.7 on 2021-10-06 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0034_auto_20211006_0857'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='search_data',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
