from automationcommon.models import clear_local_user, set_local_user


class RequestUserMiddleware(object):
    """
    Middleware that simply set's the request.user to be used for the audit trail.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
    
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
