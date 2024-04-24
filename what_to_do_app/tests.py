import pytest
from django.test import Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import AnonymousUser
from datetime import datetime
from .views import DayView, WeekView, SummaryDetailView
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

def test_login_success(client_with_login, test_user):
    login_url = reverse('login')
    success_url = reverse('current_day')
    data = {'username': 'test_user', 'password': 'test_password'}

    response = client_with_login.post(login_url, data=data, follow=True)

    assert response.status_code == 200
    assert response.resolver_match.url_name == 'current_day'

def test_login_failure(client, test_user):
    login_url = reverse('login')
    #  use incorrect data for login
    data = {'username': 'test_user', 'password': 'wrong_password'}

    response = client.post(login_url, data=data, follow=True)
    # after failed login attempt we should remain on login page
    assert response.status_code == 200
    assert response.resolver_match.url_name == 'login'


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


@pytest.mark.django_db
class TestDayView:
    # define setup method that will run on start of every test
    # create instance of test client and test user
    def setup_method(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')

    def test_get_method_without_date(self):
        # test get method without date parameter
        url = reverse('current_day')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_get_method_with_date(self):
        # test 'get' method with date parameter
        date_str = datetime.now().strftime('%Y-%m-%d')
        url = reverse('day', kwargs={'date': date_str})
        response = self.client.get(url, {'date': date_str})
        assert response.status_code == 200


@pytest.mark.django_db
def test_add_activity_post():
    client = Client()

    # create new user and login
    user = CustomUser.objects.create_user(username='test_user', password='12345')
    client.login(username='test_user', password='12345')

    # create form data and invoke POST method with form data
    form_data = {'name': 'Test Activity', 'description': 'This is a test activity'}
    response = client.post(reverse('add_activity'), data=form_data)

    # check if form is sent correctly und user is redirected
    assert response.status_code == 302

    # check if activity added correctly to database
    assert Activity.objects.filter(name='Test Activity').exists()

# fixtures and test for week_view
@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(username='user1', password='pass')


@pytest.fixture
def activity(db, user):
    return Activity.objects.create(user=user, name='Test Activity')


@pytest.fixture
def activity_event(db, user, activity):
    return ActivityEvent.objects.create(activity=activity, user=user, activity_date='2023-01-01')


@pytest.fixture
def view(db, user):
    # create GET request to /week_view/
    factory = RequestFactory()
    request = factory.get('/week_view/')
    # set user of request for test user
    request.user = user
    # create object WeekView and set its request and kwargs
    view = WeekView()
    view.request = request
    view.kwargs = {'date': '2023-01-01'}
    return view


def test_get_context_data(db, view, user, activity, activity_event):
    context = view.get_context_data(date='2023-01-01')
    # test if context has correct keys and if their values are not None
    assert context['start_week'] is not None
    assert context['end_week'] is not None
    assert context['week_dates_with_activities'] is not None
    assert context['prev_week'] is not None
    assert context['next_week'] is not None




@pytest.mark.django_db
def test_summary_detail_view():
    # Create test user and log in
    test_user = CustomUser.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    # Create a day summary for the user
    date = datetime.now().date()
    test_summary = "This is a test summary."
    DaySummary.objects.create(user=test_user, date=date, summary=test_summary)

    # Get the response from the server
    response = client.get('/summary-detail', {'date': date})

    # Check the status code
    assert response.status_code == 200

    # Check the content
    assert test_summary in str(response.content)

    # Check if the correct template was used
    assert 'summary_details.html' in [template.name for template in response.templates]


@pytest.mark.django_db
def test_day_summary_pdf_view():
    # create test user and summary
    test_user = CustomUser.objects.create_user(username='test_user', password='test_pass')
    test_day_summary = DaySummary.objects.create(user=test_user, date='2024-04-04', summary='This is a test summary.')

    client = Client()

    logged_in = client.login(username='test_user', password='test_pass')
    assert logged_in is True

    #  generate URL for view and pass ID of created  test_day_summary object and send GET request
    url = reverse('day-summary-pdf', kwargs={'summary_id': test_day_summary.id})
    response = client.get(url)

    # check if response is correct
    assert response.status_code == 200

    # check if response content type is PDF
    assert response['content-type'] == 'application/pdf'

    # make sure that pDF file was successfully created
    assert b'%PDF' in response.content

