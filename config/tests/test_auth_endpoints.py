import json

import pytest
from faker import Faker


@pytest.mark.django_db
def test_signup(client, user_factory, django_user_model):
    user_data = user_factory.build()
    password = Faker().password()
    payload = {
        "password_2": password,
        "email": user_data.email,
        "phone_number": user_data.phone_number,
        "password": password,
    }
    response = client.post(
        path="/api/auth/signup/",
        data=payload,
    )
    assert response.status_code == 201

    response_data = response.json()
    registered_user = django_user_model.objects.get(email=response_data["email"])
    assert (
        response_data["email"] == registered_user.email
        and response_data["phoneNumber"] == registered_user.phone_number
    )


@pytest.mark.django_db
def test_get_token(client, user_factory):
    user = user_factory.create()
    password = Faker().password()
    user.set_password(password)
    assert user.check_password(password)
    user.save()

    response = client.post(
        path="/api/auth/get-token/", data={"email": user.email, "password": password}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "access" in response_data.keys()


@pytest.mark.django_db
def test_change_email(client, user_factory):
    user = user_factory.create()
    password = Faker().password()
    user.set_password(password)
    assert user.check_password(password)
    user.save()

    response = client.post(
        path="/api/auth/get-token/", data={"email": user.email, "password": password}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "access" in response_data.keys()
    access_token = response_data["access"]

    new_email = "test.new.email@google.com"
    response = client.patch(
        path="/api/auth/change-email/",
        data={"email": new_email},
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.email == new_email
