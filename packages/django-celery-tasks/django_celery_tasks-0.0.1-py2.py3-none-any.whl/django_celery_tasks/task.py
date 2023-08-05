from celery import Task
from .middleware.globalrequestmiddleware import GlobalRequestMiddleware

from .models import TaskResult


class OperationTask(Task):
    operation_model = TaskResult

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None,
                    link=None, link_error=None, shadow=None, **options):
        if not self.operation_model:
            raise ValueError('The django model for this operation must be defined.')
        if not task_id:
            signature = self.signature(args=args, kwargs=kwargs, producer=producer,
                                       link=link, link_error=link_error, shadow=shadow, **options)
            signature.freeze()
            return signature.apply_async()
        else:
            request = GlobalRequestMiddleware.get_current_request()
            self.operation_model(
                task_id=task_id,
                task_name=self.name,
                task_args=args,
                task_kwargs=kwargs,
                user=request.user if not request.user.is_anonymous else None,
            ).save()
            return super(OperationTask, self).apply_async(args=args, kwargs=kwargs, task_id=task_id, producer=producer,
                                                          link=link, link_error=link_error, shadow=shadow, **options)
