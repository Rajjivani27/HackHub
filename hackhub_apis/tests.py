from django.test import TestCase
from rest_framework.test import APIClient,APITestCase
from django.urls import reverse
from .models import *

class PostTests(TestCase):
    def test_post_listview(self):
        response = self.client.get(reverse("posts-list"))
        self.assertEqual(response.status_code,200)

# Create your tests here.
