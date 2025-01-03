# merchants/management/commands/generate_orders.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from merchants.models import Merchant, MenuItem
from orders.models import Order, OrderItem
from decimal import Decimal
from datetime import datetime, timedelta
import random
import pytz

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates realistic order data for demo purposes'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_count = 0
        self.service_fee = Decimal('2000.00')

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to generate orders for'
        )
        parser.add_argument(
            '--merchant',
            type=int,
            help='Merchant ID to generate orders for'
        )

    def generate_time_for_date(self, date):
        """Generate realistic order time based on typical meal times"""
        # Define peak hours (breakfast, lunch, dinner)
        peak_hours = [
            (7, 10),   # Breakfast: 7 AM - 10 AM
            (11, 14),  # Lunch: 11 AM - 2 PM
            (17, 21),  # Dinner: 5 PM - 9 PM
        ]
        
        # Higher chance of orders during peak hours
        if random.random() < 0.8:  # 80% chance of peak hour order
            peak = random.choice(peak_hours)
            hour = random.randint(peak[0], peak[1])
        else:
            # Non-peak hours (excluding late night)
            hour = random.randint(7, 21)
        
        minute = random.randint(0, 59)
        return date.replace(hour=hour, minute=minute)

    def generate_order_items(self, menu_items):
        """Generate realistic order items"""
        # Most orders have 1-3 items
        num_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 20, 7, 3])[0]
        selected_items = random.sample(list(menu_items), num_items)
        
        order_items = []
        total_amount = Decimal('0.00')
        
        for item in selected_items:
            # Generate realistic quantities (usually 1-2 per item)
            quantity = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
            subtotal = item.price * quantity
            
            order_items.append({
                'menu_item': item,
                'quantity': quantity,
                'price': item.price,
                'subtotal': subtotal
            })
            total_amount += subtotal
        
        # Add service fee
        total_amount += self.service_fee
        
        return order_items, total_amount

    def generate_user_note(self):
        """Generate realistic user notes"""
        notes = [
            "Mohon cabainya level sedang ya",
            "Tolong bungkus rapi",
            "Jangan pedas",
            "Extra pedas ya",
            "Tidak pakai sayur",
            "Tidak pakai bawang",
            "Nasi setengah porsi saja",
            "",  # Empty note
            "",
            ""  # Higher chance of no notes
        ]
        return random.choice(notes)

    def handle(self, *args, **options):
        days = options['days']
        merchant_id = options['merchant']

        try:
            if merchant_id:
                merchant = Merchant.objects.get(id=merchant_id)
                merchants = [merchant]
                self.stdout.write(f'Generating orders for merchant: {merchant.name}')
            else:
                merchants = Merchant.objects.filter(is_active=True)
                self.stdout.write(f'Generating orders for {len(merchants)} merchants')

            if not merchants:
                self.stdout.write(self.style.ERROR('No merchants found'))
                return

            # Get users who are not merchants
            customer_users = User.objects.filter(is_merchant=False)
            if not customer_users:
                self.stdout.write(self.style.ERROR('No customer users found'))
                return

            today = timezone.now()
            self.order_count = 0

            for merchant in merchants:
                self.stdout.write(f'Processing merchant: {merchant.name}')
                menu_items = list(MenuItem.objects.filter(merchant=merchant, is_available=True))
                
                if not menu_items:
                    self.stdout.write(
                        self.style.WARNING(f'No menu items found for merchant {merchant.name}')
                    )
                    continue

                # Generate orders for each day
                for day in range(days):
                    date = today - timedelta(days=day)
                    
                    # Generate more orders on weekends
                    base_orders = random.randint(5, 12)
                    weekend_multiplier = 1.5 if date.weekday() >= 5 else 1
                    num_orders = int(base_orders * weekend_multiplier)
                    
                    with transaction.atomic():
                        for _ in range(num_orders):
                            try:
                                # Generate order items first
                                order_items, total_amount = self.generate_order_items(menu_items)
                                order_time = self.generate_time_for_date(date)
                                
                                # Create order with all necessary data
                                order = Order.objects.create(
                                    user=random.choice(customer_users),
                                    merchant=merchant,
                                    status='completed',
                                    payment_status='paid',
                                    total_amount=total_amount,
                                    note=self.generate_user_note(),
                                    created_at=order_time,
                                    updated_at=order_time
                                )

                                # Create order items
                                for item_data in order_items:
                                    OrderItem.objects.create(
                                        order=order,
                                        menu_item=item_data['menu_item'],
                                        quantity=item_data['quantity'],
                                        price=item_data['price'],
                                        subtotal=item_data['subtotal']
                                    )

                                self.order_count += 1

                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(f'Error creating order: {str(e)}')
                                )
                                continue

                # Update merchant's total_orders
                merchant.total_orders = Order.objects.filter(
                    merchant=merchant,
                    payment_status='paid'
                ).count()
                merchant.save()
                
                self.stdout.write(
                    f'Generated {self.order_count} orders for {merchant.name}'
                )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully generated {self.order_count} total orders')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating orders: {str(e)}')
            )