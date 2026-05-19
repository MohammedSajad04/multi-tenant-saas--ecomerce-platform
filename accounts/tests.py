from rest_framework.test import APITestCase

from .models import User


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='mobile_user',
            email='hancock@example.com',
            password='123456',
            role='customer',
        )

    def test_login_with_username(self):
        response = self.client.post(
            '/api/accounts/login/',
            {'username': self.user.username, 'password': '123456'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_requires_username(self):
        response = self.client.post(
            '/api/accounts/login/',
            {'email': self.user.email, 'password': '123456'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
