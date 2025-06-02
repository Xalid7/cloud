from django.contrib import admin
from .models import Customer, Deal, Task, Product

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email']
    list_filter = ['created_at']

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'area', 'appointment_date', 'price', 'status']
    list_filter = ['status', 'appointment_date']
    search_fields = ['name', 'customer__name']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'due_date', 'status', 'created_at']
    list_filter = ['status', 'due_date']
    search_fields = ['title', 'description']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity']
    list_filter = ['category']
    search_fields = ['name']