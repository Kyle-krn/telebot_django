# Generated by Django 3.2.8 on 2021-12-07 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_shop', '0006_alter_ordersiteproduct_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordersiteproduct',
            name='pay_url',
            field=models.CharField(blank=True, help_text='Url оплаты в QIWI', max_length=250, null=True),
        ),
    ]
