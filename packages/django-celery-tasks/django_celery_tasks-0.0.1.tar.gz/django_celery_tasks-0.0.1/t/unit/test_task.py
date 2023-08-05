from __future__ import absolute_import, unicode_literals
from builtins import str

import pytest

from django.test import Client, TestCase
from django.contrib.auth.models import User

from django_celery_tasks.models import TaskResult


@pytest.mark.usefixtures('depends_on_current_app')
class TaskTest(TestCase):

    @pytest.fixture(autouse=True)
    def setup_app(self, app):
        self.app = app
        self.app.conf.result_serializer = 'pickle'
        self.app.conf.result_backend = (
            'django_celery_tasks.backends:DatabaseBackend')

    def setUp(self):
        User.objects.create_user(username='testuser', email='test@user.com', password='12345')
        self.client = Client()

    def test_requesttask(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/task')
        task = TaskResult.objects.get_task(str(response.content, 'utf-8'))
        user = User.objects.get(username='testuser')
        assert task.user == user
