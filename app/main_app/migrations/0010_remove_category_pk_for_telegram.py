# Generated by Django 3.2.8 on 2021-11-14 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_orderingproduct_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='pk_for_telegram',
        ),
    ]
