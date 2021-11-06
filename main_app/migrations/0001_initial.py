# Generated by Django 3.2.8 on 2021-11-06 01:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Имя категории', max_length=255)),
                ('photo', models.ImageField(help_text='Фото категории', upload_to='category_img/')),
                ('slug', models.CharField(blank=True, help_text='Используется в боте для поиска категории', max_length=255, null=True, unique=True)),
                ('max_count_product', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название товара')),
                ('photo', models.ImageField(help_text='Фото товара', upload_to='product_img/')),
                ('description', models.TextField(help_text='Описание товара')),
                ('price', models.DecimalField(decimal_places=2, help_text='Цена товара', max_digits=10)),
                ('count', models.IntegerField(default=0, help_text='Остаток на складе')),
                ('slug', models.CharField(blank=True, help_text='Слаг товара', max_length=255, null=True, unique=True)),
                ('weight', models.IntegerField(help_text='Вес товара')),
            ],
        ),
        migrations.CreateModel(
            name='QiwiToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.BigIntegerField(blank=True, null=True)),
                ('balance', models.IntegerField(blank=True, null=True)),
                ('token', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=False)),
                ('blocked', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.IntegerField(help_text='Id пользователя телеграм', unique=True)),
                ('first_name', models.CharField(blank=True, help_text='Имя', max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, help_text='Фамилия', max_length=255, null=True)),
                ('username', models.CharField(blank=True, help_text='Юзернейм', max_length=255, null=True)),
                ('fio', models.CharField(blank=True, help_text='ФИО для доставки', max_length=255, null=True)),
                ('address', models.TextField(blank=True, help_text='Адрес доставки', null=True)),
                ('number', models.BigIntegerField(blank=True, help_text='Телефон пользователя', null=True)),
                ('post_index', models.IntegerField(blank=True, help_text='Почтовый индекс', null=True)),
                ('search_data', models.CharField(blank=True, help_text='Данные для поиска товара', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TelegramProductCartCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=1, help_text='Кол-во товара')),
                ('counter', models.BooleanField(default=True, help_text='Если True, берет значение count для отображения в клавиатуре')),
                ('product', models.ForeignKey(help_text='Товар', on_delete=django.db.models.deletion.CASCADE, to='main_app.product')),
                ('user', models.ForeignKey(help_text='Юзер', on_delete=django.db.models.deletion.CASCADE, to='main_app.telegramuser')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Имя подкатегории', max_length=150)),
                ('photo', models.ImageField(help_text='Фотоподкатегории', upload_to='subcategory_img/')),
                ('slug', models.CharField(blank=True, help_text='Слаг подкатегории', max_length=255, null=True, unique=True)),
                ('category', models.ForeignKey(help_text='Категория подкатегории', on_delete=django.db.models.deletion.CASCADE, to='main_app.category')),
            ],
        ),
        migrations.CreateModel(
            name='SoldProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, help_text='Цена на момент продажи', max_digits=10)),
                ('count', models.IntegerField(help_text='Кол-во проданного товара')),
                ('date', models.DateTimeField(auto_now_add=True, help_text='Дата и время продажи')),
                ('payment_bool', models.BooleanField(default=False, help_text='Произведена ли оплата')),
                ('product', models.ForeignKey(help_text='Продукт', on_delete=django.db.models.deletion.CASCADE, to='main_app.product')),
            ],
        ),
        migrations.CreateModel(
            name='ReceptionProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(blank=True, help_text='Заметка приемки', max_length=255, null=True)),
                ('price', models.DecimalField(decimal_places=2, help_text='Закупочная цена', max_digits=10)),
                ('count', models.IntegerField(help_text='Кол-во товара в приемке')),
                ('date', models.DateTimeField(auto_now_add=True, help_text='Дата и время приемки')),
                ('liquidated', models.BooleanField(default=False, help_text='Ликвидация товара')),
                ('product', models.ForeignKey(help_text='Товар', on_delete=django.db.models.deletion.CASCADE, to='main_app.product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(help_text='Подкатегория товара', on_delete=django.db.models.deletion.CASCADE, to='main_app.subcategory'),
        ),
        migrations.CreateModel(
            name='PayProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_pay', models.IntegerField()),
                ('pay_comment', models.CharField(max_length=255)),
                ('delivery_pay', models.IntegerField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.telegramuser')),
            ],
        ),
        migrations.CreateModel(
            name='OrderingProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_pay', models.IntegerField(help_text='Стоимость доставки')),
                ('track_code', models.BigIntegerField(blank=True, help_text='Трек-код заказа', null=True)),
                ('check_admin', models.BooleanField(default=False)),
                ('datetime', models.DateTimeField(auto_now_add=True, help_text='Дата и время создания заказа')),
                ('fio', models.CharField(blank=True, help_text='ФИО для доставки', max_length=255, null=True)),
                ('address', models.TextField(blank=True, help_text='Адрес доставки', null=True)),
                ('number', models.BigIntegerField(blank=True, help_text='Номер телефона пользователя', null=True)),
                ('post_index', models.BigIntegerField(blank=True, help_text='Почтовый индекс', null=True)),
                ('payment_bool', models.BooleanField(default=False, help_text='Оплачен ли заказ')),
                ('qiwi_bool', models.BooleanField(default=False, help_text='Способ оплаты - киви')),
                ('sold_product', models.ManyToManyField(help_text='Товары в заказе', to='main_app.SoldProduct')),
                ('user', models.ForeignKey(help_text='Юзер', on_delete=django.db.models.deletion.CASCADE, to='main_app.telegramuser')),
            ],
        ),
    ]
