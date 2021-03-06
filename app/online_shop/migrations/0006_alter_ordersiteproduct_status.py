# Generated by Django 3.2.8 on 2021-12-07 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_shop', '0005_ordersiteproduct_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordersiteproduct',
            name='status',
            field=models.CharField(choices=[('Awaiting payment', 'Ожидает оплаты'), ('Created', 'Созданно'), ('Processing', 'В процессе'), ('Shipped', 'Доставляется'), ('Ready for pickup', 'Ожидает получения'), ('Completed', 'Доставленно')], default='Awaiting payment', max_length=20),
        ),
    ]
