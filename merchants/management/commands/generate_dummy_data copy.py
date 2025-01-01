from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from merchants.models import Merchant, Category, MenuItem
from faker import Faker
import random

User = get_user_model()
fake = Faker('id_ID')  # Menggunakan locale Indonesia

class Command(BaseCommand):
    help = 'Generates dummy data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating dummy data...')

        # Create categories
        categories = [
            'Makanan Berat',
            'Makanan Ringan',
            'Minuman',
            'Dessert',
            'Snack',
            'Nasi',
            'Mie',
            'Sayuran',
            'Seafood',
            'Daging'
        ]
        
        category_objects = []
        for cat_name in categories:
            category, created = Category.objects.get_or_create(name=cat_name)
            category_objects.append(category)
            if created:
                self.stdout.write(f'Created category: {cat_name}')

        # Create merchant users and merchants
        for i in range(20):  # Create 20 merchants
            # Create user for merchant
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = fake.user_name()
                
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                is_merchant=True,
                phone_number=fake.phone_number(),
                address=fake.address()
            )

            # Create merchant
            merchant = Merchant.objects.create(
                user=user,
                name=f"{fake.company()} {random.choice(['Warung', 'Kantin', 'Resto', 'Café'])}",
                description=fake.text(max_nb_chars=200),
                is_active=True
            )
            self.stdout.write(f'Created merchant: {merchant.name}')

            # Create menu items for each merchant
            num_items = random.randint(5, 15)  # Each merchant has 5-15 menu items
            for j in range(num_items):
                MenuItem.objects.create(
                    merchant=merchant,
                    category=random.choice(category_objects),
                    name=fake.catch_phrase()[:50],  # Limit name length
                    description=fake.text(max_nb_chars=100),
                    price=random.randint(5000, 100000),  # Price between 5k-100k
                    is_available=random.choice([True, True, True, False])  # 75% chance of being available
                )

        # Create regular users
        for i in range(30):  # Create 30 regular users
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = fake.user_name()
                
            User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                is_merchant=False,
                phone_number=fake.phone_number(),
                address=fake.address()
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data'))
        self.stdout.write('You can login to any merchant or user account with:')
        self.stdout.write('Username: [generated username]')
        self.stdout.write('Password: password123')