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
            username = "Tester Guy",
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
            #location = "Test City"
        )
    
        self.project1.tasks.add(self.task1)

    def test_project_view_offer_response(self):

        user2 = User.objects.create_user(
            username = "Testoline",
            password = "qwerty123",
        )
        taskOffer1 = TaskOffer.objects.create(
            task = self.task1,
            title = "Great offer",
            description = "Will clean",
            price = 450,
            offerer = user2.profile, #User.objects.last().profile,
            status = 'p',
            feedback = ''
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
            username = "Testoline",
            password = "qwerty123",
        )
        taskOffer1 = TaskOffer.objects.create(
            task = self.task1,
            title = "Great offer",
            description = "Will clean",
            price = 450,
            offerer = user2.profile, #User.objects.last().profile,
            status = 'p',
            feedback = ''
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
            username = "Testoline",
            password = "qwerty123",
        )
        taskOffer1 = TaskOffer.objects.create(
            task = self.task1,
            title = "Great offer",
            description = "Will clean",
            price = 450,
            offerer = user2.profile, #User.objects.last().profile,
            status = 'p',
            feedback = ''
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
            username = "Testoline",
            password = "qwerty123",
        )
        request = self.client.get('/projects/' + str(self.project1.id) + '/')
        assert(request.status_code == 200)

        #return statement 1: if user == task.project.user.user
        assert(self.user1 == self.task1.project.user.user)
        response = get_user_task_permissions(self.user1, self.task1)
        assert(response['write'] == True)
        assert(response['read'] == True)
        assert(response['modify'] == True)
        assert(response['owner'] == True)
        assert(response['upload'] == True)

    def test_get_user_task_permissions_task_offerer(self):
        #return statement 2: if task.accepted_task_offer() and task.accepted_task_offer().offerer == user.profile
        user2 = User.objects.create_user(
            username = "Testoline",
            password = "qwerty123",
        )
        self.taskOffer1 = TaskOffer.objects.create(
            task = self.task1,
            title = "Great offer",
            description = "Will clean",
            price = 450,
            offerer = user2.profile, #User.objects.last().profile,
            status = 'a',
            feedback = ''
        )

        request = self.client.get('/projects/' + str(self.project1.id) + '/')
        assert(request.status_code == 200)
        self.task1.project.user.user = self.user1
        self.task1.accepted_task_offer().offerer = user2.profile #Profile.objects.first()
        assert(user2 != self.task1.project.user.user)
        assert(self.task1.accepted_task_offer() and self.task1.accepted_task_offer().offerer == user2.profile)
        response = get_user_task_permissions(user2, self.task1)
        assert(response['write'] == True)
        assert(response['read'] == True)
        assert(response['modify'] == True)
        assert(response['owner'] == False)
        assert(response['upload'] == True)

    def test_get_user_task_permissions_else(self):
        user2 = User.objects.create_user(
            username = "Testoline",
            password = "qwerty123",
        )
        response = get_user_task_permissions(user2, self.task1)
        assert(response['write'] == False)
        assert(response['read'] == False)
        assert(response['modify'] == False)
        assert(response['owner'] == False)
        assert(response['upload'] == False)

