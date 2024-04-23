import pytest
from django.test import Client
from django.urls import reverse
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


@pytest.fixture
def test_user(db):
    return get_user_model().objects.create_user(username='test_user', password='test_password')

@pytest.fixture
def client_with_login(test_user):
    client = Client()
    client.login(username='test_user', password='test_password')
    return client

def test_login_success(client, test_user):
    login_url = reverse('login')
    success_url = reverse('current_day')
    data = {'username': 'test_user', 'password': 'test_password'}

    response = client.post(login_url, data=data, follow=True)

    assert response.status_code == 200
    assert response.resolver_match.url_name == 'current_day'




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


@pytest.mark.django_db
def test_activity_update_view(client):
    # create test user and activity
    test_user = CustomUser.objects.create_user(username='test_user', password='test_password')
    activity = Activity.objects.create(user=test_user, name='Activity 1')

    # login user
    client.login(username='test_user', password='test_password')

    url = reverse('activity_update', kwargs={'pk': activity.pk})
    response = client.get(url)

    # check the status code of the response and if the correct template is used
    assert response.status_code == 200
    assert 'activity_form.html' in response.templates[0].name

    response = client.post(url, {'user': test_user.pk, 'name': 'Updated Activity'})  # update the activity

    # check if redirected after successful form submission
    assert response.status_code == 302
    assert response.url == reverse('activity_list')

    # check if activity data was updated correctly
    activity.refresh_from_db()
    assert activity.name == 'Updated Activity'


