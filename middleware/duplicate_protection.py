import hashlib
import time
from flask import request, jsonify
from functools import wraps

# In-memory cache for request hashes (for simplicity; use Redis in production)
request_cache = {}
CACHE_EXPIRY = 300  # 5 minutes

def duplicate_protection(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Create a hash of the request data
        request_data = str(request.get_json()) + request.url + request.method
        request_hash = hashlib.sha256(request_data.encode()).hexdigest()

        current_time = time.time()

        # Check if hash exists and is not expired
        if request_hash in request_cache:
            if current_time - request_cache[request_hash] < CACHE_EXPIRY:
                return jsonify({'error': 'Duplicate request detected'}), 429
            else:
                # Expired, remove it
                del request_cache[request_hash]

        # Store the hash with current time
        request_cache[request_hash] = current_time

        return f(*args, **kwargs)
    return wrapper