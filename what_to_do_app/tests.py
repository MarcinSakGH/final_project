import pytest
from django.test import Client, TestCase, RequestFactory
from django.urls import reverse
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from .views import DayView
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
    username = ''
    password = ''

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


@pytest.mark.django_db
def test_CustomUserUpdateView(client):
    test_user = CustomUser.objects.create_user(username='test_user', password='test_password')
    url = reverse('user-update')
    client.login(username='test_user', password='test_password')

    response = client.get(url)
    assert response.status_code == 200

    assert 'form' in response.context

    new_first_name = 'new_test_first_name'
    response = client.post(url, {'first_name': new_first_name,
                                 'username': test_user.username,
                                })
    print(response.content)
    assert response.status_code == 302  # check if redirected after updating the data
    assert response.url == reverse('home')  # check if redirects to correct site


@pytest.mark.django_db
def test_activities_view_authenticated_user():
    client = Client()
    CustomUser.objects.create_user(username='test_user', password='test_password')
    client.login(username='test_user', password='test_password')
    response = client.get(reverse('activity_list'))
    print(response.content)
    assert response.status_code == 200
    assert 'activities' in response.context  # check if 'activities' available in context of response


@pytest.mark.django_db
def test_activities_view_not_authenticated_user():
    client = Client()
    response = client.get(reverse('activity_list'))
    print(response.content)
    assert response.status_code == 302  # check if unauthorized users are redirected

class DayViewTestCase(TestCase):
    def setUp(self):
        self.day_view = DayView()

    def test_day_status_today(self):
        today = datetime.today().date()
        status = self.day_view.day_status(today)
        self.assertEqual(status, 'Today')

    def test_day_status_tomorrow(self):
        tomorrow = datetime.today().date() + timedelta(days=1)
        status = self.day_view.day_status(tomorrow)
        self.assertEqual(status, 'Tomorrow')

    def test_day_status_yesterday(self):
        yesterday = datetime.today().date() - timedelta(days=1)
        status = self.day_view.day_status(yesterday)
        self.assertEqual(status, 'Yesterday')
