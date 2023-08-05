import threading


class GlobalRequestMiddleware:
    _threadmap = {}

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    @classmethod
    def get_current_request(cls):
        try:
            return cls._threadmap[threading.current_thread().ident]
        except KeyError:
            return None

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        self._threadmap[threading.current_thread().ident] = request
        try:

            response = self.get_response(request)

            # Code to be executed for each request/response after
            # the view is called.

            return response
        finally:
            try:
                del self._threadmap[threading.current_thread().ident]
            except KeyError:
                pass
