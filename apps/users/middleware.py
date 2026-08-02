import logging
import time

logger = logging.getLogger("blog")


class RequestLoggingMiddleware:
    """Logs every incoming request/response at INFO level, and errors at ERROR level."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start) * 1000

        log_level = logging.INFO
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING

        logger.log(
            log_level,
            "%s %s -> %s (%.1fms)",
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
        )
        return response
