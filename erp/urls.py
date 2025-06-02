from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('deals/', views.deals_list, name='deals_list'),
    path('deals/new/', views.deal_create, name='deal_create'),
    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks/new/', views.task_create, name='task_create'),
    path('products/', views.products_list, name='products_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
]