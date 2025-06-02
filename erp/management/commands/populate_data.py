from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from erp.models import Customer, Deal, Task, Product


class Command(BaseCommand):
    help = 'Populate the database with dummy data for the clothes shop ERP'

    def handle(self, *args, **options):
        self.stdout.write('Creating dummy data...')

        # Create customers
        customers_data = [
            {
                'name': 'Deanna Annis',
                'email': 'deannannis@gmail.com',
                'phone': '999-999-9999',
                'address': '475 Spruce Drive, Pittsburgh, PA 23592'
            },
            {
                'name': 'George Gamble',
                'email': 'goeorgegamble@gmail.com',
                'phone': '999-999-9999',
                'address': '2213 Thorn Street, Glenrock, WY 12345'
            },
            {
                'name': 'Andrea Willis',
                'email': 'andreawillis@gmail.com',
                'phone': '999-999-9999',
                'address': '1952 Chicago Avenue, Fresno, PA 93721'
            },
            {
                'name': 'Brent Rodrigues',
                'email': 'brodrigues@gmail.com',
                'phone': '555-123-4567',
                'address': '789 Oak Street, Denver, CO 80202'
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@email.com',
                'phone': '555-987-6543',
                'address': '321 Pine Avenue, Seattle, WA 98101'
            },
            {
                'name': 'Michael Chen',
                'email': 'mchen@email.com',
                'phone': '555-456-7890',
                'address': '456 Maple Street, Portland, OR 97201'
            },
            {
                'name': 'Emily Davis',
                'email': 'emily.davis@email.com',
                'phone': '555-321-6547',
                'address': '789 Elm Avenue, Austin, TX 78701'
            },
            {
                'name': 'David Wilson',
                'email': 'dwilson@email.com',
                'phone': '555-654-3210',
                'address': '123 Cedar Lane, Miami, FL 33101'
            },
        ]

        customers = []
        for customer_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                email=customer_data['email'],
                defaults=customer_data
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'Created customer: {customer.name}')

        # Create deals
        deals_data = [
            {
                'name': '475 Spruce Drive, Pittsburgh, PA 23592',
                'area': '100M²',
                'price': 6000,
                'status': 'in_progress'
            },
            {
                'name': '1952 Chicago Avenue, Fresno, CA 93721',
                'area': '100M²',
                'price': 6000,
                'status': 'closed'
            },
            {
                'name': '4409 Haul Road, Saint Paul, MN 55102',
                'area': '100M²',
                'price': 6000,
                'status': 'in_progress'
            },
            {
                'name': '579 Godfrey Street, Monitor, OR 97071',
                'area': '100M²',
                'price': 6000,
                'status': 'closed'
            },
            {
                'name': '2705 Cantebury Drive, New York, NY 10011',
                'area': '100M²',
                'price': 6000,
                'status': 'in_progress'
            },
            {
                'name': '319 Haul Road, Glenrock, WY 12345',
                'area': '100M²',
                'price': 5750,
                'status': 'closed'
            },
            {
                'name': '47 Spruce Drive, Quantico, VA',
                'area': '100M²',
                'price': 5750,
                'status': 'closed'
            },
            {
                'name': '165 Belmont Drive, Parowan, UT',
                'area': '100M²',
                'price': 5750,
                'status': 'closed'
            },
            {
                'name': '1538 Hammer Road, Cleveland, OH',
                'area': '100M²',
                'price': 5750,
                'status': 'closed'
            },
        ]

        for i, deal_data in enumerate(deals_data):
            appointment_date = timezone.now() + timedelta(days=random.randint(-30, 30))
            deal, created = Deal.objects.get_or_create(
                name=deal_data['name'],
                defaults={
                    **deal_data,
                    'appointment_date': appointment_date,
                    'customer': customers[i % len(customers)]
                }
            )
            if created:
                self.stdout.write(f'Created deal: {deal.name}')

        # Create tasks
        tasks_data = [
            {
                'title': 'Meeting with partners',
                'description': 'Quarterly business review meeting with key partners',
                'status': 'overdue'
            },
            {
                'title': 'Web conference agenda (overdue)',
                'description': 'Prepare comprehensive agenda for upcoming web conference',
                'status': 'overdue'
            },
            {
                'title': 'Meeting with partners',
                'description': 'Follow-up meeting with business partners to discuss new opportunities',
                'status': 'completed'
            },
            {
                'title': 'Add new services',
                'description': 'Research and add new clothing alteration services to our offerings',
                'status': 'pending'
            },
            {
                'title': 'Upload new legals (terms & conditions)',
                'description': 'Update website with new legal documents and terms of service',
                'status': 'completed'
            },
            {
                'title': 'Sales report due',
                'description': 'Prepare comprehensive monthly sales report for management',
                'status': 'pending'
            },
            {
                'title': 'Lunch with Steve',
                'description': 'Business lunch meeting with potential supplier Steve',
                'status': 'pending'
            },
            {
                'title': 'Weekly meeting',
                'description': 'Team weekly sync meeting to discuss progress and challenges',
                'status': 'pending'
            },
            {
                'title': 'Inventory audit',
                'description': 'Complete quarterly inventory audit for all product categories',
                'status': 'pending'
            },
            {
                'title': 'Customer feedback review',
                'description': 'Review and analyze customer feedback from last month',
                'status': 'completed'
            },
        ]

        for i, task_data in enumerate(tasks_data):
            if task_data['status'] == 'overdue':
                due_date = timezone.now() - timedelta(days=random.randint(1, 10))
            elif task_data['status'] == 'completed':
                due_date = timezone.now() - timedelta(days=random.randint(1, 30))
            else:
                due_date = timezone.now() + timedelta(days=random.randint(1, 30))

            task, created = Task.objects.get_or_create(
                title=task_data['title'],
                defaults={
                    **task_data,
                    'due_date': due_date
                }
            )
            if created:
                self.stdout.write(f'Created task: {task.title}')

        # Create products
        products_data = [
            {
                'name': 'Cotton T-Shirt',
                'category': 'shirts',
                'price': 29.99,
                'stock_quantity': 150,
                'description': 'Comfortable 100% cotton t-shirt available in multiple colors and sizes'
            },
            {
                'name': 'Denim Jeans',
                'category': 'pants',
                'price': 79.99,
                'stock_quantity': 75,
                'description': 'Classic denim jeans with modern fit and premium quality'
            },
            {
                'name': 'Summer Dress',
                'category': 'dresses',
                'price': 89.99,
                'stock_quantity': 50,
                'description': 'Light and airy summer dress perfect for warm weather occasions'
            },
            {
                'name': 'Leather Jacket',
                'category': 'jackets',
                'price': 199.99,
                'stock_quantity': 25,
                'description': 'Premium leather jacket with classic styling and superior craftsmanship'
            },
            {
                'name': 'Silk Scarf',
                'category': 'accessories',
                'price': 39.99,
                'stock_quantity': 100,
                'description': 'Elegant silk scarf with beautiful patterns and luxurious feel'
            },
            {
                'name': 'Wool Sweater',
                'category': 'shirts',
                'price': 69.99,
                'stock_quantity': 80,
                'description': 'Cozy wool sweater perfect for cold weather'
            },
            {
                'name': 'Chino Pants',
                'category': 'pants',
                'price': 59.99,
                'stock_quantity': 90,
                'description': 'Versatile chino pants suitable for casual and business casual wear'
            },
            {
                'name': 'Evening Gown',
                'category': 'dresses',
                'price': 299.99,
                'stock_quantity': 15,
                'description': 'Elegant evening gown for special occasions and formal events'
            },
            {
                'name': 'Bomber Jacket',
                'category': 'jackets',
                'price': 129.99,
                'stock_quantity': 35,
                'description': 'Trendy bomber jacket with modern design and comfortable fit'
            },
            {
                'name': 'Designer Belt',
                'category': 'accessories',
                'price': 79.99,
                'stock_quantity': 60,
                'description': 'High-quality leather belt with designer buckle'
            },
            {
                'name': 'Polo Shirt',
                'category': 'shirts',
                'price': 45.99,
                'stock_quantity': 120,
                'description': 'Classic polo shirt made from premium cotton blend'
            },
            {
                'name': 'Cargo Shorts',
                'category': 'pants',
                'price': 39.99,
                'stock_quantity': 85,
                'description': 'Practical cargo shorts with multiple pockets'
            },
            {
                'name': 'Cocktail Dress',
                'category': 'dresses',
                'price': 149.99,
                'stock_quantity': 30,
                'description': 'Stylish cocktail dress perfect for parties and social events'
            },
            {
                'name': 'Windbreaker',
                'category': 'jackets',
                'price': 89.99,
                'stock_quantity': 45,
                'description': 'Lightweight windbreaker jacket for outdoor activities'
            },
            {
                'name': 'Luxury Watch',
                'category': 'accessories',
                'price': 299.99,
                'stock_quantity': 20,
                'description': 'Premium timepiece with elegant design and precise movement'
            },
            {
                'name': 'Flannel Shirt',
                'category': 'shirts',
                'price': 54.99,
                'stock_quantity': 70,
                'description': 'Warm flannel shirt perfect for casual wear'
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with dummy data!')
        )