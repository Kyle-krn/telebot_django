# Generated by Django 3.2.8 on 2021-11-28 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0013_auto_20211128_2016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderingproduct',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Цена на момент продажи', max_digits=10, null=True),
        ),
    ]
