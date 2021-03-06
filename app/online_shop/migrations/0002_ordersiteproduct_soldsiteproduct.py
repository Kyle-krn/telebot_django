# Generated by Django 3.2.8 on 2021-11-28 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0013_auto_20211128_2016'),
        ('online_shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderSiteProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('telephone', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=250)),
                ('postal_code', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=100)),
                ('note', models.TextField(blank=True)),
                ('transport_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('track_code', models.BigIntegerField(blank=True, help_text='Трек-код заказа', null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Created', 'Created'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Ready for pickup', 'Ready for pickup'), ('Completed', 'Completed')], default='Created', max_length=20)),
                ('price', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SoldSiteProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, help_text='Цена на момент продажи', max_digits=10)),
                ('count', models.IntegerField(help_text='Кол-во проданного товара')),
                ('date', models.DateTimeField(auto_now_add=True, help_text='Дата и время продажи')),
                ('order', models.ForeignKey(help_text='Заказ', on_delete=django.db.models.deletion.CASCADE, to='online_shop.ordersiteproduct')),
                ('product', models.ForeignKey(help_text='Продукт', on_delete=django.db.models.deletion.CASCADE, to='main_app.product')),
            ],
        ),
    ]
