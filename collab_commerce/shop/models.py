from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Avg, Count
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from decimal import Decimal

def generate_secret_code():
    return uuid.uuid4().hex[:8].upper()

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_list_by_category', args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=100)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    # New fields for reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]

    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def update_ratings(self):
        """Recalculates and updates the average rating and review count."""
        reviews = self.reviews.all()
        self.review_count = reviews.count()
        if self.review_count > 0:
            self.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        else:
            self.average_rating = 0
        self.save()


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)]) # 1 to 5 stars
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('product', 'user') # Each user can only review a product once

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'

class ShoppingGroup(models.Model):
    name = models.CharField(max_length=100)
    secret_code = models.CharField(max_length=12, unique=True, default=generate_secret_code)
    members = models.ManyToManyField(User, related_name='shopping_groups')
    shared_cart = models.OneToOneField('Cart', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return sum(item.get_total() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def get_total(self):
        return self.product.price * self.quantity
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField()

    def __str__(self):
        return self.code

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    group = models.ForeignKey('ShoppingGroup', on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    cashfree_order_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True, on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    def get_total_cost_after_discount(self):
        return self.total_price - (self.total_price * (self.discount / Decimal(100)))

    def __str__(self):
        return f"Order {self.id} for {self.group.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

class ChatMessage(models.Model):
    group = models.ForeignKey(ShoppingGroup, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message[:20]}'

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, related_name='status_history', on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name_plural = 'Order Status Histories'

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=ShoppingGroup)
def create_group_cart(sender, instance, created, **kwargs):
    if created and not instance.shared_cart:
        cart = Cart.objects.create()
        instance.shared_cart = cart
        instance.save()

@receiver([post_save, post_delete], sender=Review)
def update_product_ratings(sender, instance, **kwargs):
    """
    A signal that automatically updates the product's average rating
    and review count whenever a review is added or deleted.
    """
    instance.product.update_ratings()
