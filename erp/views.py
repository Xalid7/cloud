from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import Customer, Deal, Task, Product
from .forms import CustomerForm, DealForm, TaskForm, ProductForm


def dashboard(request):
    # Get statistics
    total_customers = Customer.objects.count()
    total_deals = Deal.objects.count()
    total_tasks = Task.objects.count()
    total_products = Product.objects.count()

    # Get next appointment
    next_appointment = Deal.objects.filter(
        appointment_date__gte=timezone.now()
    ).order_by('appointment_date').first()

    # Get recent deals
    recent_deals = Deal.objects.order_by('-created_at')[:4]

    # Get recent customers
    recent_customers = Customer.objects.order_by('-created_at')[:3]

    # Get upcoming tasks
    upcoming_tasks = Task.objects.filter(
        status='pending'
    ).order_by('due_date')[:6]

    context = {
        'total_customers': total_customers,
        'total_deals': total_deals,
        'total_tasks': total_tasks,
        'total_products': total_products,
        'next_appointment': next_appointment,
        'recent_deals': recent_deals,
        'recent_customers': recent_customers,
        'upcoming_tasks': upcoming_tasks,
    }
    return render(request, 'erp/dashboard.html', context)


def customers_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    total_customers = customers.count()

    context = {
        'customers': customers,
        'total_customers': total_customers,
    }
    return render(request, 'erp/customers.html', context)


def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('customers_list')
    else:
        form = CustomerForm()

    return render(request, 'erp/customer_form.html', {'form': form})


def deals_list(request):
    deals = Deal.objects.all().order_by('-created_at')
    total_deals = deals.count()

    context = {
        'deals': deals,
        'total_deals': total_deals,
    }
    return render(request, 'erp/deals.html', context)


def deal_create(request):
    if request.method == 'POST':
        form = DealForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deal created successfully!')
            return redirect('deals_list')
    else:
        form = DealForm()

    return render(request, 'erp/deal_form.html', {'form': form})


def tasks_list(request):
    tasks = Task.objects.all().order_by('due_date')
    total_tasks = tasks.count()

    # Update overdue tasks
    for task in tasks:
        if task.is_overdue() and task.status != 'overdue':
            task.status = 'overdue'
            task.save()

    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
    }
    return render(request, 'erp/tasks.html', context)


def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task created successfully!')
            return redirect('tasks_list')
    else:
        form = TaskForm()

    return render(request, 'erp/task_form.html', {'form': form})


def products_list(request):
    products = Product.objects.all().order_by('-created_at')
    total_products = products.count()

    # Calculate total inventory value
    total_value = sum(product.price * product.stock_quantity for product in products)

    # Low stock products (less than 10 items)
    low_stock_count = products.filter(stock_quantity__lt=10).count()

    context = {
        'products': products,
        'total_products': total_products,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'erp/products.html', context)


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('products_list')
    else:
        form = ProductForm()

    return render(request, 'erp/product_form.html', {'form': form})


def reports(request):
    # Date range for reports (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    # Sales data
    deals_this_month = Deal.objects.filter(
        created_at__gte=start_date,
        status='closed'
    )
    total_sales = deals_this_month.aggregate(Sum('price'))['price__sum'] or 0
    deals_count = deals_this_month.count()

    # Customer growth
    new_customers = Customer.objects.filter(created_at__gte=start_date).count()

    # Task completion rate
    completed_tasks = Task.objects.filter(
        created_at__gte=start_date,
        status='completed'
    ).count()
    total_tasks_period = Task.objects.filter(created_at__gte=start_date).count()
    completion_rate = (completed_tasks / total_tasks_period * 100) if total_tasks_period > 0 else 0

    # Product categories performance
    category_sales = {}
    for choice in Product.CATEGORY_CHOICES:
        category = choice[0]
        category_products = Product.objects.filter(category=category)
        category_sales[choice[1]] = sum(p.price * (100 - p.stock_quantity) for p in category_products)

    # Monthly sales data for chart
    monthly_sales = []
    for i in range(12):
        month_start = end_date.replace(day=1) - timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)
        month_sales = Deal.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end,
            status='closed'
        ).aggregate(Sum('price'))['price__sum'] or 0
        monthly_sales.append({
            'month': month_start.strftime('%b'),
            'sales': float(month_sales)
        })

    monthly_sales.reverse()

    context = {
        'total_sales': total_sales,
        'deals_count': deals_count,
        'new_customers': new_customers,
        'completion_rate': round(completion_rate, 1),
        'category_sales': category_sales,
        'monthly_sales': monthly_sales,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'erp/reports.html', context)


def settings(request):
    if request.method == 'POST':
        # Handle settings update
        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')

    # Get current settings (you can expand this with actual settings model)
    settings_data = {
        'company_name': 'Fashion Forward Boutique',
        'company_email': 'info@fashionforward.com',
        'company_phone': '+1 (555) 123-4567',
        'company_address': '123 Fashion Street, Style City, SC 12345',
        'currency': 'USD',
        'timezone': 'America/New_York',
        'notifications_enabled': True,
        'email_notifications': True,
        'sms_notifications': False,
    }

    context = {
        'settings': settings_data,
    }
    return render(request, 'erp/settings.html', context)