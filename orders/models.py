from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User
from merchants.models import MenuItem, Merchant

# orders/models.py

from django.db import models
from django.contrib.auth import get_user_model
from merchants.models import MenuItem

User = get_user_model()



class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_amount(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def __str__(self):
        return f"Cart - {self.user.username}"

from django.core.exceptions import ValidationError

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Check if cart already has items from different merchant
        if self.cart.items.exists():
            first_item = self.cart.items.first()
            if first_item.menu_item.merchant != self.menu_item.merchant:
                raise ValidationError("Tidak bisa menambahkan menu dari kantin berbeda")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_subtotal(self):
        return self.menu_item.price * self.quantity

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

from django.db import models
from django.utils import timezone

# orders/models.py
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    midtrans_id = models.CharField(max_length=100, blank=True)
    payment_url = models.CharField(max_length=255, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
        
    def cancel(self):
        self.status = 'cancelled'
        self.payment_status = 'expired'
        self.save()

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

        
    @property
    def is_expired(self):
        """Check if order is older than 24 hours"""
        return timezone.now() > self.created_at + timedelta(hours=24)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"