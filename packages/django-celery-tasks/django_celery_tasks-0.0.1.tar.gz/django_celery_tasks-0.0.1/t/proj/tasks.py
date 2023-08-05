from __future__ import absolute_import
from celery import shared_task
from django_celery_tasks.task import OperationTask


@shared_task(bind=True, base=OperationTask)
def test_task(self):
    return True
