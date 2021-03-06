from automationcommon.models import clear_local_user, set_local_user


class RequestUserMiddleware(object):
    """
    Middleware that simply set's the request.user to be used for the audit trail.
    """
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        # If we're being called as a new-style middleware then get_response
        # should have been passed to us in __init__.
        assert self.get_response is not None
        self.process_request(request)
        response = self.get_response(request)
        return self.process_response(request, response)

    @classmethod
    def process_request(cls, request):
        set_local_user(request.user)

    @classmethod
    def process_response(cls, request, response):
        """
        Clear the user to minimise the chance of a user being wrongly assigned.
        """
        clear_local_user()
        return response

    @classmethod
    def process_exception(cls, request, exception):
        """
        Clear the user to minimise the chance of a user being wrongly assigned.
        """
        clear_local_user()
