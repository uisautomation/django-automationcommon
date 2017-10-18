import threading

# a thread local object used for binding the django request.user to the thread
thread_local = threading.local()


class RequestUserMiddleware(object):

    @classmethod
    def process_request(cls, request):
        """
        Middleware that simply bind the request.user to the request's thread.
        """
        thread_local.request_user = None if request.user.is_anonymous() else request.user


def get_request_user():
    """
    :return: The user for the local thread's request
    """
    return thread_local.request_user if hasattr(thread_local, 'request_user') else None
