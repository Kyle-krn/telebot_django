# Generated by Django 3.2.7 on 2021-10-07 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0038_qiwitoken_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='qiwitoken',
            name='blocked',
            field=models.BooleanField(default=False),
        ),
    ]
