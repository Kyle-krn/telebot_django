# Generated by Django 3.2.8 on 2021-10-22 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OfflineCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Имя категории', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OfflineSubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Имя подкатегории', max_length=150)),
                ('category', models.ForeignKey(help_text='Категория подкатегории', on_delete=django.db.models.deletion.CASCADE, to='seller_site.offlinecategory')),
            ],
        ),
        migrations.CreateModel(
            name='OfflineProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название товара')),
                ('price', models.DecimalField(decimal_places=2, help_text='Цена товара', max_digits=10)),
                ('count', models.IntegerField(default=0, help_text='Остаток на складе')),
                ('subcategory', models.ForeignKey(help_text='Подкатегория товара', on_delete=django.db.models.deletion.CASCADE, to='seller_site.offlinesubcategory')),
            ],
        ),
    ]