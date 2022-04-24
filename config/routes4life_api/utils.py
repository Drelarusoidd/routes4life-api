import random
import string
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ResetCodeManager:
    __storage = {}
    __ttl = timedelta(minutes=2)

    @classmethod
    def get_or_create_code(cls, email: str) -> str:
        if cls.__storage.get(email, None) is not None and cls.check_code_ttl(email):
            return cls.__storage[email][0]
        return cls.__regenerate_code(email)

    @classmethod
    def check_code_ttl(cls, email: str) -> bool:
        try:
            return cls.__storage[email][1] + cls.__ttl > timezone.now()
        except KeyError:
            return False

    @classmethod
    def __regenerate_code(cls, email: str) -> str:
        code = "".join(random.choices(string.digits, k=4))
        timestamp = timezone.now()
        cls.__storage[email] = (code, timestamp)
        return cls.__storage[email][0]

    @classmethod
    def __remove_code(cls, email: str):
        if cls.__storage.get(email, None) is not None:
            cls.__storage.pop(email)

    @classmethod
    def try_use_code(cls, email: str, code: str) -> bool:
        """Any time we use this method the code bound to email is deleted."""
        try:
            code_with_timestamp = cls.__storage.get(email, None)
            if code_with_timestamp is None or not cls.check_code_ttl(email):
                return False
            code_from_storage = code_with_timestamp[0]
            if code_from_storage != code:
                return False
        finally:
            try:
                cls.__storage.pop(email)
            except KeyError:
                pass
        return True


class SessionTokenManager:
    __storage = {}
    __ttl = timedelta(minutes=10)

    @classmethod
    def check_token_ttl(cls, email: str) -> bool:
        try:
            return cls.__storage[email][1] + cls.__ttl > timezone.now()
        except KeyError:
            return False

    @classmethod
    def get_or_create_token(cls, email: str) -> str:
        if cls.__storage.get(email, None) is not None:
            return cls.__storage[email][0]
        token = "".join(random.choices(string.digits + string.ascii_letters, k=32))
        timestamp = timezone.now()
        cls.__storage[email] = (token, timestamp)
        return cls.__storage[email][0]

    @classmethod
    def try_use_token(cls, email: str, token: str) -> bool:
        """Any time we use this method the token bound to email is deleted."""
        try:
            token_with_timestamp = cls.__storage.get(email, None)
            if token_with_timestamp is None or not cls.check_token_ttl(email):
                return False
            token_from_storage = token_with_timestamp[0]
            if token_from_storage != token:
                return False
        finally:
            try:
                cls.__storage.pop(email)
            except KeyError:
                pass
        return True
