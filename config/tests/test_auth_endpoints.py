import json

import pytest
from faker import Faker


@pytest.mark.django_db
def test_signup(client, user_factory, django_user_model):
    fake = Faker()
    user_data = user_factory.build()
    password = fake.password()
    response = client.post(
        path="/api/auth/signup/",
        data={
            "email": user_data.email,
            "phone_number": user_data.phone_number,
            "password": password,
            "password_2": password,
        },
    )
    assert response.status_code == 201

    response_data = response.json()
    user = django_user_model.objects.get(email=response_data["email"])
    assert (
        response_data["email"] == user.email
        and response_data["phoneNumber"] == user.phone_number
    )

    # Signup with existing email
    password = fake.password()
    response = client.post(
        path="/api/auth/signup/",
        data={
            "email": user_data.email,
            "phone_number": fake.msisdn(),
            "password": password,
            "password_2": password,
        },
    )
    assert response.status_code == 400
    assert len(django_user_model.objects.all()) == 1


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
    fake = Faker()
    user = user_factory.create()
    password = fake.password()
    user.set_password(password)
    assert user.check_password(password)
    user.save()

    response = client.post(
        path="/api/auth/get-token/", data={"email": user.email, "password": password}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "access" in response_data.keys()
    access_token = response_data["access"]  # token obtained

    # Normal request
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

    # Existing email
    old_email = user.email
    new_email = "test.new.email.2@google.com"
    user2 = user_factory.create()
    password = fake.password()
    user2.set_password(password)
    assert user2.check_password(password)
    user2.email = new_email
    user2.save()

    response = client.patch(
        path="/api/auth/change-email/",
        data={"email": new_email},
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 400
    assert user.email == old_email


@pytest.mark.django_db
def test_change_password(client, user_factory):
    fake = Faker()
    user = user_factory.create()
    password = fake.password()
    new_password = fake.password()
    user.set_password(password)
    assert user.check_password(password)
    user.save()

    response = client.post(
        path="/api/auth/get-token/", data={"email": user.email, "password": password}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "access" in response_data.keys()
    access_token = response_data["access"]  # token obtained

    # Unauthorized
    response = client.patch(
        path="/api/auth/change-password/",
        data={
            "password": password,
            "newPassword": new_password,
            "newPassword2": new_password,
        },
    )
    assert response.status_code == 401

    # Normal request
    response = client.patch(
        path="/api/auth/change-password/",
        data={
            "password": password,
            "newPassword": new_password,
            "newPassword2": new_password,
        },
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 200
    password = new_password
    user.refresh_from_db()
    assert user.check_password(password)

    # Non-matching passwords
    response = client.patch(
        path="/api/auth/change-password/",
        data={
            "password": password,
            "newPassword": new_password + "nonmatch",
            "newPassword2": new_password,
        },
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_reset_password_flow(client, user_factory):
    fake = Faker()
    user = user_factory.create()
    password = fake.password()
    new_password = fake.password()
    user.set_password(password)
    assert user.check_password(password)
    user.save()
