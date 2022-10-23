import pytest


@pytest.fixture  # из pytest получаем фикстуру
@pytest.mark.django_db  # декоратор, который накатит миграции и после окончания тестирования откатит
def hr_token(client, django_user_model):  # аргумент user из django, не экспортировать собственного user-а
    username = 'hr'
    password = '12345'

    django_user_model.objects.create_user(  # модель user-а сделаем объект и вызываем у него метод create_user
        username=username,
        password=password,
        role="hr"  # только hr может создавать вакансии
    )

    response = client.post(  # запрос на логин
        "/user/login/",
        {
            "username": username,
            "password": password
        },
        format='json'
    )

    return response.data["token"]  # из запроса вытащить поле токен
