import logging
import time
from datetime import datetime
from collections import defaultdict
from django.http import HttpResponseForbidden

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


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour  

        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden("Access to the chat is restricted during these hours.")

        return self.get_response(request)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_request_log = defaultdict(list)
        self.max_requests = 5   
        self.time_window = 60   

    def __call__(self, request):
        if request.method == "POST":
            ip = self.get_client_ip(request)
            now = time.time()

            recent_requests = [
                t for t in self.ip_request_log[ip] if now - t < self.time_window
            ]
            self.ip_request_log[ip] = recent_requests

            if len(recent_requests) >= self.max_requests:
                return HttpResponseForbidden(
                    "Message limit exceeded. Please wait before sending more messages."
                )

            self.ip_request_log[ip].append(now)

        return self.get_response(request)
    

class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required.")

        user_role = getattr(request.user, "role", None)

        if user_role not in ["admin", "moderator"]:
            return HttpResponseForbidden("You do not have permission to access this resource.")

        return self.get_response(request)