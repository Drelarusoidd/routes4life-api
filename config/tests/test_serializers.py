import pytest
from faker import Faker
from routes4life_api.models import User
from routes4life_api.serializers import (
    RegisterUserSerializer,
    UpdateEmailSerializer,
    UserInfoSerializer,
)


@pytest.mark.django_db
def test_register_user_serializer(user_factory):
    user_data = user_factory.build()
    password = "123456789"
    serializer = RegisterUserSerializer(
        data={
            "email": user_data.email,
            "phone_number": user_data.phone_number,
            "password": password,
            "password_2": password,
        }
    )
    assert serializer.is_valid()
    new_user = serializer.save()
    assert User.objects.filter(email=new_user.email).exists()


@pytest.mark.django_db
def test_update_email_serializer(user_factory):
    test_user = user_factory.create()
    password = "123456789"
    old_email = test_user.email

    test_user.set_password(password)
    assert test_user.check_password(password)

    fake = Faker()
    serializer = UpdateEmailSerializer(instance=test_user, data={"email": fake.email()})
    assert serializer.is_valid()
    new_email = serializer.save().email
    assert old_email != new_email


@pytest.mark.django_db
def test_user_info_serializer(user_factory):
    test_user = user_factory.create()
    password = "123456789"

    old_email = test_user.email
    old_fname = test_user.first_name
    old_lname = test_user.last_name
    old_phone = test_user.phone_number

    test_user.set_password(password)
    assert test_user.check_password(password)

    fake = Faker()
    serializer = UserInfoSerializer(
        instance=test_user,
        data={
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "phone_number": fake.msisdn(),
        },
    )
    assert serializer.is_valid()
    serializer.save()
    assert (
        test_user.email == old_email
        and test_user.first_name != old_fname
        and test_user.last_name != old_lname
        and test_user.phone_number != old_phone
    )

    old_phone = test_user.phone_number
    serializer = UserInfoSerializer(
        instance=test_user, data={"phone_number": fake.msisdn()}, partial=True
    )
    assert serializer.is_valid()
    serializer.save()
    assert test_user.email == old_email and test_user.phone_number != old_phone
