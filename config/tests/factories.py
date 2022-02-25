import factory
from faker import Faker
from routes4life_api.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = fake.email()
    first_name = fake.first_name()
    last_name = fake.last_name()
    phone_number = fake.msisdn()
    is_staff = "False"
    is_superuser = "False"
