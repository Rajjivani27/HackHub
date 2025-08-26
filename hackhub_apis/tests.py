from django.test import TestCase
from rest_framework.test import APIClient,APITestCase
from django.urls import reverse
from .models import *

class CustomUserTests(APITestCase):
    def setUp(self):
        CustomUser.objects.create_user(email = "testuser@gmail.com",username="testuser",password="testing321@")

    def test_check_user_exist(self):
        user = CustomUser.objects.get(email = "testuser@gmail.com")

    def test_token_api(self):
        url = reverse("token_obtain_api")
        data = {"email": "testuser@gmail.com","password":"testing321@"}
        token = self.client.post(url,data,format="json")
        self.assertEqual(token.status_code,200)
        self.assertIn("access",token.data)
        self.refresh = token.data.get('refresh')

        """
        Checking for refresh endpoint here because of the nature of Django Tests

        Each test case here is isolated from each other.
        
        For ex. test_check_user_exist() and test_token_api() are isolated from each other.

        Means if a class variable is set in one method then it will be reinitiated to its,
        default value in other test case.

        That's why checking both token endpoints checking here only.
        """

        url = reverse("token_refresh_api")
        data = {"refresh":self.refresh}
        token = self.client.post(url,data,format="json")
        self.assertEqual(token.status_code,200)
        self.assertIn("access",token.data)
        


class PostTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="testuser@gmail.com",username="testuser",password="testing321")
        self.post = Post.objects.create(title="Hello",content = "World",author = self.user)

    def test_post_listview(self):
        response = self.client.get(reverse("posts-list"))
        self.assertEqual(response.status_code,200)

    def test_post_retrive_view(self):
        url = reverse("posts-detail" , args=[self.post.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['title'],'Hello')
        

# Create your tests here.
