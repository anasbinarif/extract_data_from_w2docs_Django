from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import CustomUser


class YourViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create(username='testuser', email='test@example.com')
        self.user.set_password('testpassword')
        self.user.save()
        self.token = Token.objects.create(user=self.user)

    def test_register_user(self):
        url = reverse('register')
        data = {'username': 'testuser2', 'password': 'testpassword2', 'email': 'test2@example.com'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'testpassword'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout(self):
        url = reverse('logout')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Add more test cases for other views and edge cases

# Ensure you add appropriate URLs to your Django URL configuration and adjust the reverse calls accordingly.
