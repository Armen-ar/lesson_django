import pytest

from tests.factories import VacancyFactory
from vacancies.serializers import VacancyListSerializer


@pytest.mark.django_db  # декоратор, который накатит миграции и после окончания тестирования откатит
def test_vacancy_list(client):
    vacancies = VacancyFactory.create_batch(4)  # вызывая фабрику вакансий вызываем у него метод create_batch,
    # который создаёт сразу несколько экземпляров (в данном случае 4 максимально можем задать сколько указано
    # количество на одной странице в settings.py REST_FRAMEWORK - "PAGE_SIZE": 4) можно больше (описано ниже)

    expected_response = {  # то что будем ожидать на выходе
        "count": 4,  # количество 10, потому что выше мы задали в методе create_batch
        "next": None,  # нет следующей страницы
        "previous": None,  # нет предыдущей страницы
        "results": VacancyListSerializer(vacancies, many=True).data  # в списке сериалайзер, в который передаём туда
        # список наших вакансий и укажем их многочисленность many и забираем оттуда данные списком (data)
    }

    response = client.get("/vacancy/")  # делаем get запрос на адрес /vacancy/

    assert response.status_code == 200  # проверить, что статус 200 (всё ОК)
    # assert len(response.data) == 4  # можно записать так и в create_batch и в "count" вписать
    # любое число и ниже строку закомментировать
    assert response.data == expected_response  # ожидаемые данные запроса равны данным, которые получили
