from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User
from .models import Project, Task
from .views import *
from projects.models import ProjectCategory, TaskOffer
from django.test import RequestFactory

# Create your tests here.


class Tester(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="Tester Guy",
            password="qwerty123",
        )

        self.test_category = ProjectCategory.objects.create(
            name="Cleaning"
        )

        self.project1 = Project.objects.create(
            user=self.user1.profile,
            title="Generic Project",
            description="Clean house",
            category=self.test_category,
            status='a'
        )

        self.task1 = Task.objects.create(
            project=self.project1,
            title="Testing task",
            description="This is a task",
            budget=500,
            location="Test City"
        )

        self.project1.tasks.add(self.task1)

    def test_project_view_offer_response(self):
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )
        taskOffer1 = TaskOffer.objects.create(
            task=self.task1,
            title="Great offer",
            description="Will clean",
            price_offered=450,
            offerer=user2.profile,  # User.objects.last().profile,
            status='p',
            feedback=''
        )

        factory = RequestFactory()
        request = factory.post('/projects/' + str(self.project1.id) + '/')

        request.POST = {
            'user': self.user1,
            'offer_response': 'good',
            'feedback': 'sounds good!',
            'status': 'a',
            'taskofferid': 1
        }
        request.user = self.user1
        request.method = 'POST'

        response = project_view(request, self.project1.id)

        assert(TaskOffer.objects.get(pk=1).status == 'a')

    def test_project_view_status_change(self):
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )
        taskOffer1 = TaskOffer.objects.create(
            task=self.task1,
            title="Great offer",
            description="Will clean",
            price_offered=450,
            offerer=user2.profile,  # User.objects.last().profile,
            status='p',
            feedback=''
        )

        factory = RequestFactory()
        request = factory.post('/projects/' + str(self.project1.id) + '/')

        request.POST = {
            'status_change': '',
            'status': 'i',
        }
        request.user = self.user1
        request.method = 'POST'

        response = project_view(request, self.project1.id)
        response2 = self.client.get('/projects/' + str(self.project1.id) + '/')

        assert(response2.context['project'].status == 'i')

    def test_project_view_offer_submit(self):
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )
        taskOffer1 = TaskOffer.objects.create(
            task=self.task1,
            title="Great offer",
            description="Will clean",
            price_offered=450,
            offerer=user2.profile,  # User.objects.last().profile,
            status='p',
            feedback=''
        )

        factory = RequestFactory()
        request = factory.post('/projects/' + str(self.project1.id) + '/')

        request.POST = {
            'title': 'Great offer!',
            'description': "Will clean",
            'offer_submit': '',
            'price': 300,
            'offerer': user2.profile,
            'taskvalue': self.task1.id,
            'status': 'p',
        }

        request.user = user2
        request.method = 'POST'

        response = project_view(request, self.project1.id)
        response2 = self.client.get('/projects/' + str(self.project1.id) + '/')

        assert(TaskOffer.objects.last().offerer == user2.profile)

    def test_get_user_task_permissions_project_owner(self):
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )
        request = self.client.get('/projects/' + str(self.project1.id) + '/')
        assert(request.status_code == 200)

        # return statement 1: if user == task.project.user.user
        assert(self.user1 == self.task1.project.user.user)
        response = get_user_task_permissions(self.user1, self.task1)
        assert(response['write'])
        assert(response['read'])
        assert(response['modify'])
        assert(response['owner'])
        assert(response['upload'])

    def test_get_user_task_permissions_task_offerer(self):
        '''return statement 2: if task.accepted_task_offer() and task.accepted_task_offer().offerer == user.profile'''
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )
        self.taskOffer1 = TaskOffer.objects.create(
            task=self.task1,
            title="Great offer",
            description="Will clean",
            price_offered=450,
            offerer=user2.profile,  # User.objects.last().profile,
            status='a',
            feedback=''
        )

        request = self.client.get('/projects/' + str(self.project1.id) + '/')
        assert(request.status_code == 200)
        self.task1.project.user.user = self.user1
        self.task1.accepted_task_offer().offerer = user2.profile  # Profile.objects.first()
        assert(user2 != self.task1.project.user.user)
        assert(self.task1.accepted_task_offer()
               and self.task1.accepted_task_offer().offerer == user2.profile)
        response = get_user_task_permissions(user2, self.task1)
        assert(response['write'])
        assert(response['read'])
        assert(response['modify'])
        assert(response['owner'] == False)
        assert(response['upload'])

    def test_get_user_task_permissions_else(self):
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )
        response = get_user_task_permissions(user2, self.task1)
        assert(response['write'] == False)
        assert(response['read'] == False)
        assert(response['modify'] == False)
        assert(response['owner'] == False)
        assert(response['upload'] == False)

    ################# boundary value testing ##################

    def test_boundary_project_offer_valid(self):
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )

        login_data = {
            'username': 'Testoline',
            'password': 'qwerty123'
        }

        request = self.client.post('/user/login/', login_data)
        self.assertEqual(request.status_code, 302)

        data = {
            'title': 'Testing title',
            'description': 'Testing description',
            'price_offered': 230,
            'taskvalue': self.task1.id,
            'offer_submit': ''
        }

        request2 = self.client.post(
            '/projects/' + str(self.project1.id) + '/', data)
        self.assertNotEqual(TaskOffer.objects.last(), None)

    def test_boundary_project_offer_invalid(self):
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )

        data = {
            'title': '',  # missing
            'desription': 'Testing description',
            'price_offered': 230,
            'taskvalue': int(self.task1.id),
            'offer_submit': ''
        }

        request = self.client.post(
            '/projects/' + str(self.project1.id) + '/', data)
        self.assertEqual(TaskOffer.objects.last(), None)

    ################# output coverage testing ##################

    def test_output_coverage_accepted_offer(self):
        ''' accept the project offer '''
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )
        taskOffer1 = TaskOffer.objects.create(
            task=self.task1,
            title="Great offer",
            description="Will clean",
            price_offered=450,
            offerer=user2.profile,
            status='p',
            feedback=''
        )

        login_data = {
            'username': 'Tester Guy',
            'password': 'qwerty123'
        }

        request = self.client.post('/user/login/', login_data)
        self.assertEqual(request.status_code, 302)

        data = {
            'user': self.user1,
            'offer_response': 'good',
            'feedback': 'sounds good!',
            'status': 'a',
            'taskofferid': 1
        }

        request = self.client.post(
            '/projects/' + str(self.project1.id) + '/', data)

        assert(TaskOffer.objects.last().status == 'a')

    def test_output_coverage_declined_offer(self):
        ''' decline the project offer '''
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )
        taskOffer1 = TaskOffer.objects.create(
            task=self.task1,
            title="Great offer",
            description="Will clean",
            price_offered=450,
            offerer=user2.profile,
            status='p',
            feedback=''
        )

        login_data = {
            'username': 'Tester Guy',
            'password': 'qwerty123'
        }

        request = self.client.post('/user/login/', login_data)
        self.assertEqual(request.status_code, 302)

        data = {
            'user': self.user1,
            'offer_response': 'Bad offer',
            'feedback': 'no good',
            'status': 'd',
            'taskofferid': 1
        }

        request = self.client.post(
            '/projects/' + str(self.project1.id) + '/', data)

        assert(TaskOffer.objects.last().status == 'd')

    def test_output_coverage_declined_offer_not_authenticated(self):
        ''' try to decline the project offer when not authenticated as project owner '''
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )
        taskOffer1 = TaskOffer.objects.create(
            task=self.task1,
            title="Great offer",
            description="Will clean",
            price_offered=450,
            offerer=user2.profile,
            status='p',
            feedback=''
        )

        data = {
            'user': self.user1,  # try to pass as project owner, but not authenticated through login
            'offer_response': 'Bad offer',
            'feedback': 'no good',
            'status': 'd',
            'taskofferid': 1
        }

        request = self.client.post(
            '/projects/' + str(self.project1.id) + '/', data)

        assert(TaskOffer.objects.last().status == 'p')

    ########### integration tests ############

    def test_integration_budget_feature(self):
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )

        self.assertEqual(self.project1.total_budget, 0)

        response = self.client.get('/projects/' + str(self.project1.id) + '/')

        self.assertEqual(response.context['total_budget'], 500)

        task2 = Task.objects.create(
            project=self.project1,
            title="Testing task",
            description="This is a task",
            budget=500,
        )

        self.project1.tasks.add(task2)

        response2 = self.client.get('/projects/' + str(self.project1.id) + '/')

        self.assertEquals(response2.context['total_budget'], 1000)

    def test_integration_location_feature(self):
        self.assertEqual(self.project1.tasks.last().location, "Test City")

        task2 = Task.objects.create(
            project=self.project1,
            title="Nice task",
            description="This is a task",
            budget=100,
            location="Right here",
        )

        self.project1.tasks.add(task2)

        response = self.client.get('/projects/' + str(self.project1.id) + '/')

        self.assertEqual(
            response.context['tasks'].last().location,
            "Right here")

    def test_integration_display_feature(self):
        response = self.client.get('/projects/' + str(self.project1.id) + '/')
        self.assertEqual(
            response.context['tasks'].last().location,
            "Test City")
        self.assertEqual(response.context['total_budget'], 500)

    def test_profile_feature(self):
        user2 = User.objects.create_user(
            username="Testoline",
            password="qwerty123",
        )

        login_data = {
            'username': 'Testoline',
            'password': 'qwerty123'
        }

        request = self.client.post('/user/login/', login_data)
        self.assertEqual(request.status_code, 302)

        request = self.client.get('/user/profile/')
        self.assertEqual(request.status_code, 200)

        data = {
            'username': 'TestyAndTasty',
            'first_name': 'Testy',
            'last_name': 'Test',
            'categories': 1,
            'company': 'SWECO',
            'email': 'si@gmail.com',
            'email_confirmation': 'si@gmail.com',
            'password1': 'Superuser_123',
            'password2': 'Superuser_123',
            'phone_number': 48022223,
            'country': 'Norge',
            'state': 'Fjellhamar',
            'city': 'Trondheim',
            'postal_code': 7045,
            'street_address': 'Øvre Gate Nedre'
        }

        request = self.client.post('/user/profile/', data)
        self.assertEqual(request.status_code, 302)

        login_data = {
            'username': 'TestyAndTasty',
            'password': 'Superuser_123'
        }

        # log in with new username and password
        request = self.client.post('/user/login/', login_data)
        self.assertEqual(request.status_code, 302)


'''
    def test_system(self):
        user2 = User.objects.create_user(
            username = "Testoline",
            password = "qwerty123",
        )

        false_login_data = {
            'username': 'nouser',
            'password': 'nopassword'
        }

        # hammer the website with false login attempts
        for i in range(0, 100):
            request = self.client.post('/user/login/', false_login_data)
            self.assertEqual(request.status_code, 200)

        login_data = {
            'username': 'Testoline',
            'password': 'qwerty123'
        }

        request = self.client.post('/user/login/', login_data)
        self.assertEqual(request.status_code, 302)

        data = {
            'title': 'Testing title',
            'description': 'Testing description',
            'price_offered': 200,
            'taskvalue': self.task1.id,
            'offer_submit': ''
        }

        # hammer the website with project offers
        for i in range(0, 100):
            data['price'] += i
            response = self.client.post('/projects/' + str(self.project1.id) + '/', data)
            self.assertEqual(response.status_code, 200)

'''
