# Generated by Django 3.2.8 on 2021-11-09 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0008_auto_20211109_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderingproduct',
            name='price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]