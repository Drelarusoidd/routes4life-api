import pytest
from django.contrib.auth.hashers import check_password
from faker import Faker
from routes4life_api.models import User
from routes4life_api.serializers import (
    ChangePasswordSerializer,
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

    # DON'T PASS EMPTY PHONE NUMBER
    user_data.email = ".".join(user_data.email.split(".")[:-1]) + ".exe"
    assert new_user.email != user_data.email
    password = "123456789"
    serializer = RegisterUserSerializer(
        data={
            "email": user_data.email,
            "phone_number": "  ",
            "password": password,
            "password_2": password,
        }
    )
    assert serializer.is_valid() is False

    # Right way is to completely ignore it
    serializer = RegisterUserSerializer(
        data={
            "email": user_data.email,
            "password": password,
            "password_2": password,
        }
    )
    assert serializer.is_valid()
    new_user = serializer.save()
    assert User.objects.filter(email=new_user.email).exists()
    assert new_user.phone_number == "+000000000"


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
        instance=test_user,
        data={
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
        },
    )
    assert serializer.is_valid()
    serializer.save()
    assert (
        test_user.email == old_email
        and test_user.first_name != old_fname
        and test_user.last_name != old_lname
        and test_user.phone_number == old_phone
    )

    old_phone = test_user.phone_number
    serializer = UserInfoSerializer(
        instance=test_user, data={"phone_number": fake.msisdn()}, partial=True
    )
    assert serializer.is_valid()
    serializer.save()
    assert test_user.email == old_email and test_user.phone_number != old_phone


@pytest.mark.django_db
def test_change_password_serializer(user_factory):
    test_user = user_factory.create()
    password = "123456789"
    test_user.set_password(password)
    assert test_user.check_password(password)

    # Check for normal behavior
    new_password = "234567890"
    serializer = ChangePasswordSerializer(
        instance=test_user,
        data={
            "password": password,
            "new_password": new_password,
            "new_password_2": new_password,
        },
    )
    assert serializer.is_valid()
    assert check_password(new_password, serializer.save().password)

    # Check for blank password
    password = new_password
    new_password = ""
    serializer = ChangePasswordSerializer(
        instance=test_user,
        data={
            "password": password,
            "new_password": new_password,
            "new_password_2": new_password,
        },
    )
    assert serializer.is_valid() is False

    # Check for not matching passwords
    new_password = "234567890"
    new_password_2 = "123456789"
    serializer = ChangePasswordSerializer(
        instance=test_user,
        data={
            "password": password,
            "new_password": new_password,
            "new_password_2": new_password_2,
        },
    )
    assert serializer.is_valid() is False

    # Check for wrong old password
    new_password = "234567890"
    serializer = ChangePasswordSerializer(
        instance=test_user,
        data={
            "password": "definetly_not_a_password",
            "new_password": new_password,
            "new_password_2": new_password_2,
        },
    )
    assert serializer.is_valid() is False
