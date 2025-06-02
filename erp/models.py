from django.db import models
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Deal(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]

    name = models.CharField(max_length=200)
    area = models.CharField(max_length=50)
    appointment_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def is_overdue(self):
        return self.due_date < timezone.now() and self.status != 'completed'


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('shirts', 'Shirts'),
        ('pants', 'Pants'),
        ('dresses', 'Dresses'),
        ('jackets', 'Jackets'),
        ('accessories', 'Accessories'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name