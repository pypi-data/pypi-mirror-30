from simple_django_logger.utils import Logger


class ErrorMiddleware(object):
    _initial_http_body = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    # def process_request(self, request):
    #     # this is required because for some reason there is no way to access request.body
    #     # in the 'process_exception' method.
    #     import ipdb; ipdb.set_trace()
    #     self._initial_http_body = request.body

    def process_view(self, request, callback, callback_args, callback_kwargs):
        self._initial_http_body = request.body

    def process_exception(self, request, exception):
        Logger.log_error(request, self._initial_http_body, exception)

        return None
