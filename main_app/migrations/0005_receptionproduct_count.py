# Generated by Django 3.2.5 on 2021-10-01 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_receptionproduct'),
    ]

    operations = [
        migrations.AddField(
            model_name='receptionproduct',
            name='count',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
    ]
