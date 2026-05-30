from rest_framework.test import APITestCase

from accounts.models import User
from tenants.models import Tenant
from .models import Product


class ProductTenantIsolationTests(APITestCase):

    def setUp(self):

        self.mobile_tenant = Tenant.objects.create(

            company_name='Mobile Store',
            slug='mobile-store',
            business_type='mobile',
            owner_name='Mobile Owner',
            company_email='mobile@example.com',
            phone_number='1111111111',
            address='Mobile Street',
            company_description='Phones',
            status='approved'
        )

        self.cake_tenant = Tenant.objects.create(

            company_name='Cake Shop',
            slug='cake-shop',
            business_type='cake',
            owner_name='Cake Owner',
            company_email='cake@example.com',
            phone_number='2222222222',
            address='Cake Street',
            company_description='Cakes',
            status='approved'
        )

        self.pending_tenant = Tenant.objects.create(

            company_name='Pending Perfume',
            slug='pending-perfume',
            business_type='perfume',
            owner_name='Perfume Owner',
            company_email='perfume@example.com',
            phone_number='3333333333',
            address='Perfume Street',
            company_description='Perfumes',
            status='pending'
        )

        self.mobile_admin = User.objects.create_user(

            username='mobile_admin',
            password='123456',
            role='company_admin',
            tenant=self.mobile_tenant
        )

        self.cake_admin = User.objects.create_user(

            username='cake_admin',
            password='123456',
            role='company_admin',
            tenant=self.cake_tenant
        )

        self.mobile_product = Product.objects.create(

            tenant=self.mobile_tenant,
            name='iPhone',
            description='Phone',
            category='Mobile',
            business_type='mobile',
            price='1000.00',
            stock=5
        )

        self.cake_product = Product.objects.create(

            tenant=self.cake_tenant,
            name='Chocolate Cake',
            description='Cake',
            category='Cake',
            business_type='cake',
            price='30.00',
            stock=10
        )

        self.pending_product = Product.objects.create(

            tenant=self.pending_tenant,
            name='Pending Perfume',
            description='Perfume',
            category='Perfume',
            business_type='perfume',
            price='50.00',
            stock=7
        )

    def test_company_products_only_returns_logged_in_company_products(self):

        self.client.force_authenticate(user=self.cake_admin)

        response = self.client.get('/api/products/company-products/')

        self.assertEqual(response.status_code, 200)
        product_names = {
            product['name']
            for product in response.data
        }

        self.assertEqual(product_names, {'Chocolate Cake'})

    def test_marketplace_products_only_returns_approved_company_products(self):

        response = self.client.get('/api/products/list/')

        self.assertEqual(response.status_code, 200)
        product_names = {
            product['name']
            for product in response.data
        }

        self.assertEqual(product_names, {'iPhone', 'Chocolate Cake'})
