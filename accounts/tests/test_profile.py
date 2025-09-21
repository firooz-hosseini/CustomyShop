from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="profile@test.com", password="pass123")
        self.client.force_authenticate(user=self.user)
    
    def test_get_profile(self):
        url = reverse('myuser-myuser')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)


    def test_update_profile(self):
        url = reverse('myuser-myuser')
        data = {'first_name': 'NewName'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'NewName')
        


