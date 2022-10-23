import factory.django

from authentication.models import User
from vacancies.models import Vacancy


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("name")  # у фабрики вызываем класс Faker, который принимает в свой конструктор лейбл
    # (в нашем случае это имена вымышленных пользователей) фейк имена
    password = "12345"  # обязательное поле


class VacancyFactory(factory.django.DjangoModelFactory):  # аргумент это фабрика
    class Meta:
        model = Vacancy

    slug = "test"  # обязательное поле
    text = "test text"  # обязательное поле




