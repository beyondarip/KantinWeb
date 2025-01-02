from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from merchants.models import Category, Merchant, MenuItem
from django.core.files.base import ContentFile
import requests
from decimal import Decimal
import random
from django.utils.text import slugify
from django.utils.crypto import get_random_string

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate dummy data for testing'

    def create_user(self, email, password, is_merchant=False):
        username = email.split('@')[0]  # Menggunakan bagian sebelum @ sebagai username
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            return user
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_merchant=is_merchant,
                # Tambahkan data dummy untuk field lainnya
                phone_number=f'+62812{str(random.randint(10000000, 99999999))}',
                address='Jl. Contoh No. ' + str(random.randint(1, 100))
            )
            self.stdout.write(self.style.SUCCESS(f'Created user {username}'))
            return user

    def create_categories(self):
        categories = [
            "Makanan Utama",
            "Minuman",
            "Snack",
            "Dessert",
            "Paket Hemat",
            "Menu Sehat",
            "Makanan Ringan",
            "Menu Spesial"
        ]
        
        created_categories = []
        for cat_name in categories:
            category, created = Category.objects.get_or_create(name=cat_name)
            created_categories.append(category)
            status = 'Created' if created else 'Existing'
            self.stdout.write(self.style.SUCCESS(f'{status} category: {cat_name}'))
        
        return created_categories

    def create_merchants(self, categories):
        merchant_data = [
            {
                'name': 'Warung Tegal Enak',
                'description': 'Menyajikan masakan rumahan khas Tegal yang lezat dan terjangkau.',
                'email': 'warteg.enak@example.com',
            },
            {
                'name': 'Kedai Kopi Kampus',
                'description': 'Tempat ngopi favorit mahasiswa dengan berbagai pilihan kopi dan snack.',
                'email': 'kedaikopi@example.com',
            },
            {
                'name': 'Nasi Goreng Spesial',
                'description': 'Nasi goreng dengan berbagai variasi dan tingkat kepedasan.',
                'email': 'nasgor@example.com',
            },
            {
                'name': 'Bakso Malang Pak Jo',
                'description': 'Bakso dengan kuah kaldu sapi asli dan berbagai topping.',
                'email': 'baksopakjo@example.com',
            },
            {
                'name': 'Ayam Geprek Pedas',
                'description': 'Ayam geprek dengan sambal pilihan dan level kepedasan.',
                'email': 'ayamgeprek@example.com',
            }
        ]

        created_merchants = []
        for data in merchant_data:
            # Create merchant user with unique username
            base_username = data['email'].split('@')[0]
            unique_username = f"{base_username}_{get_random_string(4)}"
            
            user = self.create_user(
                email=data['email'],
                password='password123',
                is_merchant=True
            )

            # Create merchant
            merchant, created = Merchant.objects.get_or_create(
                user=user,
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'rating': round(random.uniform(3.5, 5.0), 1),
                    'total_orders': random.randint(50, 500),
                    'is_active': True
                }
            )

            # Add random categories
            selected_categories = random.sample(categories, random.randint(2, 4))
            merchant.categories.add(*selected_categories)
            
            # Set placeholder image
            merchant_image_url = f'https://placehold.co/600x400/png?text=Restaurant+{slugify(merchant.name)}'
            try:
                response = requests.get(merchant_image_url)
                if response.status_code == 200:
                    image_name = f'{slugify(merchant.name)}.jpg'
                    merchant.image.save(image_name, ContentFile(response.content), save=True)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to set image for {merchant.name}: {e}'))

            created_merchants.append(merchant)
            status = 'Created' if created else 'Existing'
            self.stdout.write(self.style.SUCCESS(f'{status} merchant: {data["name"]}'))

        return created_merchants

    def create_menu_items(self, merchants, categories):
        menu_items_data = {
            'Makanan Utama': [
                ('Nasi Goreng Spesial', 'Nasi goreng dengan telur, ayam, dan sayuran', 15000),
                ('Mie Goreng Komplit', 'Mie goreng dengan topping lengkap', 18000),
                ('Ayam Penyet', 'Ayam penyet dengan sambal terasi', 20000),
                ('Soto Ayam', 'Soto ayam dengan kuah bening segar', 17000),
                ('Gado-gado', 'Sayuran segar dengan bumbu kacang', 15000),
            ],
            'Minuman': [
                ('Es Teh Manis', 'Teh manis dingin segar', 5000),
                ('Kopi Hitam', 'Kopi robusta pilihan', 8000),
                ('Es Jeruk', 'Jeruk segar', 6000),
                ('Es Campur', 'Campuran buah dan sirup', 12000),
                ('Jus Alpukat', 'Jus alpukat segar dengan susu', 15000),
            ],
            'Snack': [
                ('Kentang Goreng', 'Kentang goreng crispy', 10000),
                ('Pisang Goreng', 'Pisang goreng crispy', 8000),
                ('Roti Bakar', 'Roti bakar dengan berbagai topping', 12000),
                ('Dimsum', 'Aneka dimsum ayam dan udang', 15000),
                ('Cireng', 'Cireng isi dengan sambal kacang', 8000),
            ],
            'Dessert': [
                ('Es Krim', 'Es krim dengan berbagai rasa', 10000),
                ('Pancake', 'Pancake dengan maple syrup', 15000),
                ('Pudding', 'Pudding susu dengan vla', 8000),
            ],
            'Paket Hemat': [
                ('Paket Nasi Ayam', 'Nasi + Ayam + Es Teh', 25000),
                ('Paket Mie Komplit', 'Mie Goreng + Telur + Es Teh', 22000),
                ('Paket Mahasiswa', 'Nasi Goreng + Es Teh', 18000),
            ],
            'Menu Sehat': [
                ('Salad Bowl', 'Mixed salad dengan dressing', 20000),
                ('Juice Detox', 'Campuran juice sayur dan buah', 15000),
                ('Oatmeal', 'Oatmeal dengan buah segar', 18000),
            ],
            'Makanan Ringan': [
                ('Kripik Singkong', 'Kripik singkong berbagai rasa', 5000),
                ('Kacang Mix', 'Campuran kacang premium', 10000),
                ('Pop Corn', 'Pop corn caramel', 8000),
            ],
            'Menu Spesial': [
                ('Sate Ayam Spesial', 'Sate ayam dengan bumbu special', 25000),
                ('Ikan Bakar', 'Ikan bakar dengan sambal dabu-dabu', 30000),
                ('Soup Iga', 'Soup iga sapi dengan rempah', 35000),
            ]
        }

        for merchant in merchants:
            # Get categories assigned to this merchant
            merchant_categories = merchant.categories.all()
            
            for category in merchant_categories:
                # Get menu items for this category if available
                category_items = menu_items_data.get(category.name, [])
                if not category_items:
                    continue

                for item_name, description, price in category_items:
                    # Add some price variation between merchants
                    adjusted_price = price * (1 + random.uniform(-0.1, 0.1))
                    
                    menu_item, created = MenuItem.objects.get_or_create(
                        merchant=merchant,
                        name=item_name,
                        category=category,
                        defaults={
                            'description': description,
                            'price': round(Decimal(adjusted_price), -2),  # Round to nearest 100
                            'is_available': True
                        }
                    )

                    # Set placeholder image
                    if created:
                        item_image_url = f'https://placehold.co/400x300/png?text=Food+{slugify(item_name)}'
                        try:
                            response = requests.get(item_image_url)
                            if response.status_code == 200:
                                image_name = f'{slugify(item_name)}.jpg'
                                menu_item.image.save(image_name, ContentFile(response.content), save=True)
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Failed to set image for {item_name}: {e}'))

                    status = 'Created' if created else 'Existing'
                    self.stdout.write(self.style.SUCCESS(f'{status} menu item: {item_name} for {merchant.name}'))

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to generate dummy data...')
        
        # Create regular user
        self.create_user('user@example.com', 'password123')
        
        # Create categories
        categories = self.create_categories()
        
        # Create merchants
        merchants = self.create_merchants(categories)
        
        # Create menu items
        self.create_menu_items(merchants, categories)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data'))