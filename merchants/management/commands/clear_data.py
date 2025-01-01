# Buat file baru: merchants/management/commands/clear_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from merchants.models import Merchant, Category, MenuItem
from orders.models import Order, OrderItem

User = get_user_model()

class Command(BaseCommand):
    help = 'Clears all data except superuser'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing data...')
        
        # Delete all orders first (because of foreign key relationships)
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        
        # Delete menu items and merchants
        MenuItem.objects.all().delete()
        Merchant.objects.all().delete()
        Category.objects.all().delete()
        
        # Delete all users except superusers
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleared all data except superuser'))