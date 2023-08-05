from __future__ import absolute_import, unicode_literals
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .tasks import test_task


class TaskView(LoginRequiredMixin, View):
    def get(self, request):
        task = test_task.delay()
        return HttpResponse(task.id)
