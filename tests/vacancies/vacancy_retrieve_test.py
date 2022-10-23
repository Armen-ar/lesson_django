from datetime import date

import pytest


@pytest.mark.django_db  # декоратор, который накатит миграции и после окончания тестирования откатит
def test_retrieve_vacancy(client, vacancy, hr_token):
    expected_response = {
        "id": vacancy.pk,  # то, что ожидаем они динамически меняются в django
        "created": date.today().strftime("%Y-%m-%d"),  # дата создания - сегодня в виде данной строки
        "skills": [],
        "slug": "test",
        "text": "test text",
        "status": "draft",
        "min_experience": None,
        "likes": 0,
        "updated_at": None,
        "user": vacancy.user_id  # то, что ожидаем они динамически меняются в django
    }

    response = client.get(
        f"/vacancy/{vacancy.pk}/",  # get запрос на адрес vacancy/id
        HTTP_AUTHORIZATION='Token ' + hr_token  # токен авторизация получаем из фикстуры, которую сами запишем
    )

    assert response.status_code == 200  # проверить, что статус 200 (всё ОК)
    assert response.data == expected_response  # вернул данные то, что ожидали
