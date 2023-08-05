from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.contrib import admin

from .views import TaskView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^task', TaskView.as_view()),
]
