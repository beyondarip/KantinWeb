# Generated by Django 4.2.17 on 2025-01-02 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0002_alter_menuitem_image_alter_merchant_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='merchant',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='merchant',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3),
        ),
        migrations.AddField(
            model_name='merchant',
            name='total_orders',
            field=models.IntegerField(default=0),
        ),
    ]
