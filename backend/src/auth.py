from flask import request
from functools import wraps

from backend.src.config.config import CONFIG, BaseConfig


def requires_auth(func):
    if BaseConfig.DEV_STAGE:
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", None)
        if auth == "default_password":
            return func(*args, **kwargs)

    return wrapper
