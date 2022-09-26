import pytest

from tests.factories import UserFactory


# register(UserFactory)
@pytest.fixture
def user_factory():
    return UserFactory
