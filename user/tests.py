from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from .views import signup
from django.test import TestCase
from django.db import models
from projects.models import Project, Task
from projects.views import *
from projects.models import ProjectCategory, TaskOffer


# Create your tests here.
class Tester(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username = "Tester_Guy",
            password = "qwerty123",
        )

        self.test_category = ProjectCategory.objects.create(
            name =  "Cleaning"
        )

        self.project1 = Project.objects.create(
            user = self.user1.profile, #User.objects.last().profile,
            title = "Generic Project",
            description = "Clean house",
            category = self.test_category,
            status = 'a'
        )
        
        self.task1 = Task.objects.create(
            project = self.project1,
            title = "Testing task",
            description = "This is a task",
            budget = 500,
        )
        
        self.project1.tasks.add(self.task1)

    ################# boundary value testing ##################
    def test_boundary_signup_post_valid_form(self):
        data = {
            'username': 'tester12', 
            'first_name': 'Tester',
            'last_name': 'Guy',
            'categories': 1,
            'company': 'Test Inc.',
            'email': 'testerguy@gmail.com',
            'email_confirmation': 'testerguy@gmail.com',
            'password1': 'superhemmelig123',
            'password2': 'superhemmelig123',
            'phone_number': 99112233,
            'country': 'Norge',
            'state': 'Test State',
            'city': 'Test City',
            'postal_code': 1909,
            'street_address': 'Test Street 50B' 
        }

        response = self.client.post('/user/signup/', data)
        self.assertEqual(response.status_code, 302)

    def test_boundary_signup_post_invalid_form(self):
        data = {
            'username': 'tester12', 
            'first_name': 'Tester',
            'last_name': 'Guy',
            'categories': 1,
            'company': 'Test Inc.',
            'email': 'testerguy@gmail.com',
            'email_confirmation': 'testerguyulik@gmail.com',
            'password1': 'superhemmelig123',
            'password2': 'superhemmelig123ulikt',
            'phone_number': '',
            'country': 'Norge',
            'state': 'Test State',
            'city': 'Test City',
            'postal_code': 1909,
            'street_address': 'Test Street 50B' 
        }

        response = self.client.post('/user/signup/', data)
        # Assert status_code != 302 (redirect)
        self.assertEqual(response.status_code, 200)

    def test_boundary_signup_get(self):
        response = self.client.get('/user/signup/')
        self.assertEqual(response.status_code, 200)


    


