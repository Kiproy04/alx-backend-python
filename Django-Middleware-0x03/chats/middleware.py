import logging
from datetime import datetime

from django.utils.deprecation import MiddlewareMixin
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("request_logger")
        handler = logging.FileHandler("requests.log")  
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):  
        user = request.user.username if request.user.is_authenticated else "Anonymous"

        self.logger.info(
            f"{datetime.now()} - User: {user} - Path: {request.path}"
        )

        response = self.get_response(request)
        return response
