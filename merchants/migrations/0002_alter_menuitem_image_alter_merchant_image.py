# Generated by Django 4.2.17 on 2025-01-01 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='menu_items/'),
        ),
        migrations.AlterField(
            model_name='merchant',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='merchants/'),
        ),
    ]
