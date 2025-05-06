from django.utils.deprecation import MiddlewareMixin

class TrackLoggedInUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Attach the user to the request for later use
            request._logged_in_user = request.user
        else:
            request._logged_in_user = None
