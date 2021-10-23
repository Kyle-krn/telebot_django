# Generated by Django 3.2.8 on 2021-10-22 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0045_auto_20211016_0419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(help_text='Имя категории', max_length=255),
        ),
        migrations.AlterField(
            model_name='category',
            name='photo',
            field=models.ImageField(help_text='Фото категории', upload_to='category_img/'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.CharField(blank=True, help_text='Используется в боте для поиска категории', max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='address',
            field=models.TextField(blank=True, help_text='Адрес доставки', null=True),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True, help_text='Дата и время создания заказа'),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='delivery_pay',
            field=models.IntegerField(help_text='Стоимость доставки'),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='fio',
            field=models.CharField(blank=True, help_text='ФИО для доставки', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='number',
            field=models.BigIntegerField(blank=True, help_text='Номер телефона пользователя', null=True),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='payment_bool',
            field=models.BooleanField(default=False, help_text='Оплачен ли заказ'),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='post_index',
            field=models.BigIntegerField(blank=True, help_text='Почтовый индекс', null=True),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='sold_product',
            field=models.ManyToManyField(help_text='Товары в заказе', to='main_app.SoldProduct'),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='track_code',
            field=models.BigIntegerField(blank=True, help_text='Трек-код заказа', null=True),
        ),
        migrations.AlterField(
            model_name='orderingproduct',
            name='user',
            field=models.ForeignKey(help_text='Юзер', on_delete=django.db.models.deletion.CASCADE, to='main_app.telegramuser'),
        ),
        migrations.AlterField(
            model_name='product',
            name='count',
            field=models.IntegerField(default=0, help_text='Остаток на складе'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(help_text='Описание товара'),
        ),
        migrations.AlterField(
            model_name='product',
            name='photo',
            field=models.ImageField(help_text='Фото товара', upload_to='product_img/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Цена товара', max_digits=10),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.CharField(blank=True, help_text='Слаг товара', max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(help_text='Подкатегория товара', on_delete=django.db.models.deletion.CASCADE, to='main_app.subcategory'),
        ),
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.IntegerField(help_text='Вес товара'),
        ),
        migrations.AlterField(
            model_name='receptionproduct',
            name='count',
            field=models.IntegerField(help_text='Кол-во товара в приемке'),
        ),
        migrations.AlterField(
            model_name='receptionproduct',
            name='date',
            field=models.DateTimeField(auto_now_add=True, help_text='Дата и время приемки'),
        ),
        migrations.AlterField(
            model_name='receptionproduct',
            name='liquidated',
            field=models.BooleanField(default=False, help_text='Ликвидация товара'),
        ),
        migrations.AlterField(
            model_name='receptionproduct',
            name='note',
            field=models.CharField(blank=True, help_text='Заметка приемки', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='receptionproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Закупочная цена', max_digits=10),
        ),
        migrations.AlterField(
            model_name='receptionproduct',
            name='product',
            field=models.ForeignKey(help_text='Товар', on_delete=django.db.models.deletion.CASCADE, to='main_app.product'),
        ),
        migrations.AlterField(
            model_name='soldproduct',
            name='count',
            field=models.IntegerField(help_text='Кол-во проданного товара'),
        ),
        migrations.AlterField(
            model_name='soldproduct',
            name='date',
            field=models.DateTimeField(auto_now_add=True, help_text='Дата и время продажи'),
        ),
        migrations.AlterField(
            model_name='soldproduct',
            name='payment_bool',
            field=models.BooleanField(default=False, help_text='Произведена ли оплата'),
        ),
        migrations.AlterField(
            model_name='soldproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Цена на момент продажи', max_digits=10),
        ),
        migrations.AlterField(
            model_name='soldproduct',
            name='product',
            field=models.ForeignKey(help_text='Продукт', on_delete=django.db.models.deletion.CASCADE, to='main_app.product'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(help_text='Категория подкатегории', on_delete=django.db.models.deletion.CASCADE, to='main_app.category'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='name',
            field=models.CharField(db_index=True, help_text='Имя подкатегории', max_length=150),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='photo',
            field=models.ImageField(help_text='Фотоподкатегории', upload_to='subcategory_img/'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='slug',
            field=models.CharField(blank=True, help_text='Слаг подкатегории', max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='telegramproductcartcounter',
            name='count',
            field=models.IntegerField(default=1, help_text='Кол-во товара'),
        ),
        migrations.AlterField(
            model_name='telegramproductcartcounter',
            name='counter',
            field=models.BooleanField(default=True, help_text='Если True, берет значение count для отображения в клавиатуре'),
        ),
        migrations.AlterField(
            model_name='telegramproductcartcounter',
            name='product',
            field=models.ForeignKey(help_text='Товар', on_delete=django.db.models.deletion.CASCADE, to='main_app.product'),
        ),
        migrations.AlterField(
            model_name='telegramproductcartcounter',
            name='user',
            field=models.ForeignKey(help_text='Юзер', on_delete=django.db.models.deletion.CASCADE, to='main_app.telegramuser'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='address',
            field=models.TextField(blank=True, help_text='Адрес доставки', null=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='chat_id',
            field=models.IntegerField(help_text='Id пользователя телеграм', unique=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='fio',
            field=models.CharField(blank=True, help_text='ФИО для доставки', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='first_name',
            field=models.CharField(blank=True, help_text='Имя', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='last_name',
            field=models.CharField(blank=True, help_text='Фамилия', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='number',
            field=models.BigIntegerField(blank=True, help_text='Телефон пользователя', null=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='post_index',
            field=models.IntegerField(blank=True, help_text='Почтовый индекс', null=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='search_data',
            field=models.CharField(blank=True, help_text='Данные для поиска товара', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='username',
            field=models.CharField(blank=True, help_text='Юзернейм', max_length=255, null=True),
        ),
    ]