from datetime import date

import pytest


@pytest.mark.django_db  # декоратор, который накатит миграции и после окончания тестирования откатит
def test_vacancy_create(client, hr_token):
    expected_response = {  # объект вакансии
        "id": 1,
        "created": date.today().strftime("%Y-%m-%d"),  # дата создания - сегодня в виде данной строки
        "skills": [],
        "slug": "test",
        "text": "test text",
        "status": "draft",
        "min_experience": None,
        "likes": 0,
        "updated_at": None,
        "user": None
    }

    data = {  # данные, которые будем посылать в нашу ручку
        "slug": "test",  # обязательное поле
        "text": "test text",  # обязательное поле
        "status": "draft"  # обязательное поле
    }

    response = client.post(
        "/vacancy/create/",  # post запрос на адрес
        data,  # данные
        content_type='application/json',  # передаём тип данных json можно написать format='json'
        HTTP_AUTHORIZATION='Token ' + hr_token  # токен авторизация получаем из фикстуры, которую сами запишем
    )

    assert response.status_code == 201  # проверить, что статус 201 (всё создали)
    assert response.data == expected_response  # вернул данные то, что ожидали
