from automationcommon.models import clear_local_user, set_local_user


class RequestUserMiddleware(object):

    @classmethod
    def process_request(cls, request):
        """
        Middleware that simply set's the request.user to be used for the audit trail.
        """
        if request.user.is_anonymous():
            clear_local_user()
        else:
            set_local_user(request.user)
