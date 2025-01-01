from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from merchants.models import Merchant, Category, MenuItem
from faker import Faker
import random
import requests
import time

User = get_user_model()
fake = Faker('id_ID')

class Command(BaseCommand):
    help = 'Generates dummy data for testing'

    def get_random_image_url(self, type):
        # Menggunakan placeholder.com
        if type == 'merchant':
            return f"https://placehold.co/600x400/png?text=Restaurant+{random.randint(1,1000)}"
        else:  # menu item
            return f"https://placehold.co/400x300/png?text=Food+{random.randint(1,1000)}"

    def download_image(self, url, retries=3):
        """Download image with retry mechanism"""
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.content
                time.sleep(1)  # Wait before retry
            except Exception as e:
                if attempt == retries - 1:  # Last attempt
                    self.stdout.write(self.style.WARNING(f'Failed to download image after {retries} attempts: {str(e)}'))
                time.sleep(1)  # Wait before retry
        return None

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating dummy data...')

        # Create categories (kode kategori sama seperti sebelumnya)
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
        
        # Buat categories dan simpan dalam list
        category_objects = []
        for cat_name in categories:
            category, created = Category.objects.get_or_create(name=cat_name)
            category_objects.append(category)
            if created:
                self.stdout.write(f'Created category: {cat_name}')

        # Create merchants
        for i in range(20):
            self.stdout.write(f'Creating merchant {i+1}/20...')
            
            # Create user
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
            merchant_name = f"{fake.company()} {random.choice(['Warung', 'Kantin', 'Resto', 'Café'])}"
            merchant = Merchant.objects.create(
                user=user,
                name=merchant_name,
                description=fake.text(max_nb_chars=200),
                is_active=True,
            )

            # Download merchant image
            image_content = self.download_image(self.get_random_image_url('merchant'))
            if image_content:
                merchant.image.save(
                    f'merchant_{merchant.id}.png',
                    ContentFile(image_content),
                    save=True
                )

            # Create menu items
            num_items = random.randint(5, 15)
            for j in range(num_items):
                menu_item = MenuItem.objects.create(
                    merchant=merchant,
                    category=random.choice(category_objects),
                    name=fake.catch_phrase()[:50],
                    description=fake.text(max_nb_chars=100),
                    price=random.randint(5000, 100000),
                    is_available=random.choice([True, True, True, False])
                )

                # Download menu item image
                image_content = self.download_image(self.get_random_image_url('menu'))
                if image_content:
                    menu_item.image.save(
                        f'menu_item_{menu_item.id}.png',
                        ContentFile(image_content),
                        save=True
                    )

            self.stdout.write(self.style.SUCCESS(f'Created merchant: {merchant.name} with {num_items} menu items'))

        # Create regular users
        self.stdout.write('Creating regular users...')
        for i in range(30):
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