# Generated by Django 3.2.7 on 2021-10-07 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0037_qiwitoken_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='qiwitoken',
            name='balance',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
