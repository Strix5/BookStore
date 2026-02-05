from django.http import HttpResponseRedirect


class BlockAPIRouteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/ap/":  # change to /api/ when needed
            return HttpResponseRedirect("/")
        return self.get_response(request)
