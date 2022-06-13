import pytest
from faker import Faker


@pytest.mark.django_db
def test_user_settings(client, user_factory, django_user_model):
    fake = Faker()
    user = user_factory.create()
    password = fake.password()
    user.set_password(password)
    assert user.check_password(password)
    user.save()

    new_password = fake.password()
    new_first_name = "Jiabbackh"
    new_phone_number = "+3228115145"

    response = client.post(
        path="/api/auth/get-token/", data={"email": user.email, "password": password}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert "access" in response_data.keys()
    access_token = response_data["access"]

    # Unauthorized
    response = client.patch(
        path="/api/users/settings/",
        data={
            "password": password,
            "newPassword": new_password,
            "confirmationPassword": new_password,
        },
    )
    assert response.status_code == 401

    # Non-matching passwords
    response = client.patch(
        path="/api/users/settings/",
        data={
            "password": password,
            "newPassword": new_password + "nonmatch",
            "confirmationPassword": new_password,
        },
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 400
    user.refresh_from_db()
    assert user.first_name != new_first_name and user.phone_number != new_phone_number

    # Normal request
    response = client.patch(
        path="/api/users/settings/",
        data={
            "password": password,
            "newPassword": new_password,
            "confirmationPassword": new_password,
            "firstName": new_first_name,
            "phoneNumber": new_phone_number,
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
    assert user.first_name == new_first_name and user.phone_number == new_phone_number

    # Normal request without providing passwords
    new_first_name = "Rikardo"
    new_phone_number = "80294455712"
    response = client.patch(
        path="/api/users/settings/",
        data={
            "firstName": new_first_name,
            "phoneNumber": new_phone_number,
        },
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == new_first_name and user.phone_number == new_phone_number

    # Not all of the fields for password change provided
    response = client.patch(
        path="/api/users/settings/",
        data={
            "password": password,
            "newPassword": new_password,
            # confirmationPassword is missing
            "firstName": new_first_name,
            "phoneNumber": new_phone_number,
        },
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 400

    # access_token = client.post( NOTE
    #     "/api/auth/get-token/", {"email": user.email, "password": password}
    # ).json()["access"]

    response = client.get(
        "/api/users/settings/",
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 200
    user_data = response.json()
    assert (
        user_data["email"] == user.email
        and user_data["phoneNumber"] == user.phone_number
        and user_data["firstName"] == user.first_name
        and user_data["lastName"] == user.last_name
    )

    new_phone = fake.msisdn()
    new_first_name = fake.first_name()
    new_last_name = fake.last_name()

    # Full update NOTE: no avatar!!!
    response = client.patch(
        path="/api/users/settings/",
        data={
            "first_name": new_first_name,
            "last_name": new_last_name,
            "phone_number": new_phone,
        },
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 200
    user_data = response.json()
    user.refresh_from_db()
    assert (
        user_data["email"] == user.email
        and user_data["phoneNumber"] == user.phone_number
        and user_data["firstName"] == user.first_name
        and user_data["lastName"] == user.last_name
    )

    # Partial update
    new_last_name = "Sidorovich"
    response = client.patch(
        path="/api/users/settings/",
        data={
            "last_name": new_last_name,
        },
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 200
    user_data = response.json()
    user.refresh_from_db()
    assert (
        user_data["email"] == user.email
        and user_data["phoneNumber"] == user.phone_number
        and user_data["firstName"] == user.first_name
        and user_data["lastName"] == user.last_name
    )

    # Delete user
    saved_id = user.id
    response = client.delete(
        path="/api/users/settings/",
        content_type="application/json",
        **{
            "HTTP_AUTHORIZATION": f"JWT {access_token}",
        },
    )
    assert response.status_code == 204
    assert not django_user_model.objects.filter(id=saved_id).exists()
