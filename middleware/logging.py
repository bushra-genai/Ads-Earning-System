import logging
from flask import request, g
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_request_response(app):
    @app.before_request
    def log_request_info():
        g.start_time = time.time()
        logger.info(f"Request: {request.method} {request.url} - Data: {request.get_json(silent=True)}")

    @app.after_request
    def log_response_info(response):
        duration = time.time() - g.start_time
        logger.info(f"Response: {response.status_code} - Duration: {duration:.2f}s")
        return response