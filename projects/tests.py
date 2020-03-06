from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User
from .models import Project, Task
from .views import *
from projects.models import ProjectCategory, TaskOffer

# Create your tests here.

class Tester(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username = "Tester Guy",
            password = "qwerty123",
        )

        self.user2 = User.objects.create_user(
            username = "Testoline",
            password = "qwerty123",
        )

        self.test_category = ProjectCategory.objects.create(
            name =  "Cleaning"
        )

        self.project1 = Project.objects.create(
            user = self.user1.profile, #User.objects.last().profile,
            title = "Generic Project",
            description = "Clean house",
            #participants = self.user1,
            category = self.test_category
        )
        
        self.task1 = Task.objects.create(
            project = self.project1,
            title = "Testing task",
            description = "This is a task",
            budget = 500,
            location = "Test City"
        )
    
        self.project1.tasks.add(self.task1)

        self.taskOffer1 = TaskOffer.objects.create(
            task = self.task1,
            title = "Great offer",
            description = "Will clean",
            price = 450,
            offerer = User.objects.last().profile,
            status = 'a'
        )

    def test_project_view(self):
        request = self.client.get('/projects/' + str(self.project1.id) + '/')
        assert(request.status_code == 200)

        post_response = self.client.post('/projects/' + str(self.project1.id) + '/', {
            'user': self.user1,
            'offer_response': self.taskOffer1,
            'status_change': False,
        })

        response = post_response.wsgi_request
        response.user = self.user1.profile #User.objects.last().profile
        response.offer_response = self.taskOffer1

        instance = get_object_or_404(TaskOffer, id=self.taskOffer1.id)
        offer_response_form = TaskOfferResponseForm(response.POST, instance=instance)
        #print(offer_response_form)

        status_form = ProjectStatusForm(response.POST)
        #print(status_form)

        assert(response.user == self.project1.user)
        assert(response.method == 'POST')
        assert('offer_response' in response.POST)        
        #assert(offer_response_form.is_valid())
        assert(response.offer_response.status == 'a')
        assert('status_change' in response.POST)
        #assert(status_form.is_valid())

        response = project_view(response, self.project1.id)


    def test_get_user_task_permissions(self):
        #cover all return statements!

        request = self.client.get('/projects/' + str(self.project1.id) + '/')
        assert(request.status_code == 200)

        #return statement 1
        assert(self.user1 == self.task1.project.user.user)
        get_user_task_permissions(self.user1, self.task1)

        #return statement 2
        self.task1.project.user.user = self.user2
        self.task1.accepted_task_offer().offerer = self.user1.profile
        assert(self.user1 != self.task1.project.user.user)
        assert(self.task1.accepted_task_offer() and self.task1.accepted_task_offer().offerer.__str__() == self.user1.profile.__str__())
        get_user_task_permissions(self.user1, self.task1)

        #return statement 3
        self.task1.accepted_task_offer().offerer = self.user2.profile
        assert(self.user1 != self.task1.project.user.user)
        assert(self.task1.accepted_task_offer().offerer != self.user1.profile)
        get_user_task_permissions(self.user1, self.task1)

        

