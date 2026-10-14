from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegisterViewTests(TestCase):
    def test_register_creates_user(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'newuser',
                'password1': 'a-strong-pass-123',
                'password2': 'a-strong-pass-123',
            },
        )
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
