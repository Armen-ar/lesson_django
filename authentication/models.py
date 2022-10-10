from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    MALE = "m"
    FEMALE = "f"
    SEX = [(MALE, "Male"), (FEMALE, "Female")]  # список, который будет подставляться как значение для поля sex и из
    # этого списка ключом будет браться одна буковка ("m" или "f"), а в случае django for будет отображаться
    # "Male" или "Female"

    # user = models.OneToOneField(User, on_delete=models.CASCADE)  # создаётся дополнительная таблица, которая
    # # ссылается на таблицу пользователя, причём один профиль к одному пользователю. Это в случае родительского
    # класса (models.Model) с родительским классом User это поле не нужно. Но самое оптимальное наследование,
    # при котором не создаётся дополнительные таблицы это родительский класс самого User - AbstractUser. Т.е. будет
    # создаваться чистая таблица для пользователя одна единственная и в ней хранятся сразу поля из AbstractUser и поля
    # из его родительского класса AbstractBaseUser и те поля, которые здесь укажем.
    sex = models.CharField(max_length=1, choices=SEX, default=MALE)
