from rest_framework.reverse import reverse_lazy

from base.models.monitoring import Monitoring


def custom_middleware(get_response):
    # One-time configuration and initialization.
    endpoints_to_monitor = [
        "configurations-get-activites"
    ]

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        _monitor_request(request, response)

        return response

    def _monitor_request(request, response):
        for endpoint in endpoints_to_monitor:
            url = reverse_lazy(endpoint)
            if url != request.path:
                continue
            user = None
            if request.user.is_authenticated:
                user = request.user
            Monitoring.objects.create(url=url, query_params=request.GET.dict(),
                                        body=request.body.decode("utf-8"), user=user, returned_status=response.status_code)

    return middleware