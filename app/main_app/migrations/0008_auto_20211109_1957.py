# Generated by Django 3.2.8 on 2021-11-09 16:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_ordersiteproduct_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderingproduct',
            name='sold_product',
        ),
        migrations.AddField(
            model_name='soldproduct',
            name='order',
            field=models.ForeignKey(default=3, help_text='Заказ', on_delete=django.db.models.deletion.CASCADE, to='main_app.orderingproduct'),
            preserve_default=False,
        ),
    ]
