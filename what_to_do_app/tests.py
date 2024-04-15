import pytest
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import *

# Create your tests here.


@pytest.mark.django_db
def test_sign_up_view():
    client = Client()
    url = reverse('signup')
    response = client.post(url,
                           {'username': 'testuser',
                            'password1': 'passwordtest',
                            'password2': 'passwordtest',
                            })

    # check if view redirects after correctly sending the form
    assert response.status_code == 302
    assert response.url == reverse('login')

    # check if user was created correctly
    assert CustomUser.objects.filter(username='testuser').exists()

@pytest.mark.django_db
def test_activity_list_view(client):
    #  create test user
    test_user = CustomUser.objects.create_user(username='test_user', password='test_password')

    # create activity
    Activity.objects.create(user=test_user, name='Activity A')

    # login user
    client.login(username='test_user', password='test_password')

    url = reverse('activity_list')
    response = client.get(url)

    # check the status code of the response
    assert response.status_code == 200

    # check if response contains the activity data
    assert 'Activity A' in str(response.content)

    # check the number of activities in the contex of response
    assert len(response.context['activities']) == 1

class CustomLoginViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = 'test_user'
        cls.password = 'test_password'
        get_user_model().objects.create_user(username=cls.username, password=cls.password)

    def setUp(self):
        self.client = Client()

    def test_login_success(self):
        url = reverse('login')
        response = self.client.post(url, {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session['_auth_user_id'])  # user is logged

    def test_login_failure(self):
        url = reverse('login')
        response = self.client.post(url, {'username': self.username, 'password': 'wrong_password'})

        self.assertEqual(response.status_code, 200)  # after unsuccessful login stays on the same page
        self.assertEqual(self.client.session['login_attempts'], 1)  # check if 'login_attempts' is updated

