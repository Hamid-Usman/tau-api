from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

User = get_user_model()

DIETARY_CATEGORIES = [
    ('vegan', '🌱 Vegan'),
    ('vegetarian', '🥕 Vegetarian'),
    ('gluten-free', '🚫🌾 Gluten-Free'),
    ('halal', '🕌 Halal'),
    ('kosher', '✡️ Kosher'),
    ('nut-free', '🚫🥜 Nut-Free'),

    ('energy', '⚡ Energy Boosting'),
    ('focus', '🧠 Brain Fuel'),
    ('recovery', '💪 Muscle Recovery'),
    ('immunity', '🛡️ Immunity Support'),
    ('gut-health', '🦠 Gut Health'),
]

class Tag(models.Model):
    tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.tag}- {self.id}'

class FoodItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='food_images/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='food_items', blank=True)  # Track if description was auto-generated
    description_generated = models.BooleanField(default=False)

    def __str__(self):
        return self.name
class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Delivering', 'Delivering'),
        ('Delivered', 'Delivered'),
        ('Completed', 'Completed'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    order_time = models.TimeField(auto_now=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_location = models.CharField(max_length=255, blank=False, default='Not specified')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order #{self.order_time} - {self.customer.email}"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)


class Rating(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ratings')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1 to 5
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order_item', 'customer')
    def food_items(self):
        return self.order_item.name

class ReviewAgent(models.Model):
    analysis = models.CharField(max_length=5000, blank=False)
    date_created = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f'AI Review on {self.date_created}'