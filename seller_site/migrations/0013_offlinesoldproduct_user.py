# Generated by Django 3.2.8 on 2021-10-30 23:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seller_site', '0012_offlinesoldproduct_price_for_seller'),
    ]

    operations = [
        migrations.AddField(
            model_name='offlinesoldproduct',
            name='user',
            field=models.ForeignKey(default=1, help_text='Продавец', on_delete=django.db.models.deletion.PROTECT, to='auth.user'),
            preserve_default=False,
        ),
    ]