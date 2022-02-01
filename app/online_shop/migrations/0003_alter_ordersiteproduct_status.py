# Generated by Django 3.2.8 on 2021-11-28 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_shop', '0002_ordersiteproduct_soldsiteproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordersiteproduct',
            name='status',
            field=models.CharField(choices=[('Created', 'Созданно'), ('Processing', 'В процессе'), ('Shipped', 'Доставляется'), ('Ready for pickup', 'Ожидает получения'), ('Completed', 'Доставленно')], default='Created', max_length=20),
        ),
    ]