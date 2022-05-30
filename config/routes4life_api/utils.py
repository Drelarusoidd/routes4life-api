import os
import random
import string
from datetime import timedelta

# from django.conf import settings
from django.core.cache import cache
from rest_framework.views import exception_handler


class ResetCodeManager:
    __ttl = timedelta(minutes=2)

    @classmethod
    def get_or_create_code(cls, email: str) -> str:
        key = email + "__code"
        code = cache.get(key, None)
        if code is not None:
            return code
        code = "".join(random.choices(string.digits, k=4))
        cache.add(key, code, timeout=cls.__ttl.seconds)
        return cache.get(key)

    @classmethod
    def try_use_code(cls, email: str, code: str) -> bool:
        key = email + "__code"
        if cache.get(key) != code:
            return False
        cache.delete(key)
        return True


class SessionTokenManager:
    __ttl = timedelta(minutes=10)

    @classmethod
    def get_or_create_token(cls, email: str) -> str:
        key = email + "__token"
        token = cache.get(key, None)
        if token is not None:
            return token
        token = "".join(random.choices(string.digits + string.ascii_letters, k=32))
        cache.add(key, token, timeout=cls.__ttl.seconds)
        return cache.get(key)

    @classmethod
    def try_use_token(cls, email: str, token: str) -> bool:
        key = email + "__token"
        if cache.get(key) != token:
            return False
        cache.delete(key)
        return True


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        newdata = dict()
        newdata["errors"] = []
        for err in response.data.values():
            if isinstance(err, (list, tuple)):
                newdata["errors"].extend(err)
            else:
                newdata["errors"].append(err)
        response.data = newdata
    return response


def upload_avatar_to(instance, filename):
    return (
        # f"{settings.UPLOAD_ROOT}/{instance.email.replace('@', 'AT')}"
        f"{instance.email.replace('@', 'AT')}"
        + f"/avatar{os.path.splitext(filename)[1]}"
    )
