# Generated by Django 3.2.3 on 2021-09-13 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_remove_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.CharField(default='', max_length=1000),
            preserve_default=False,
        ),
    ]
