def test_a():
    assert True


def test_root_not_found(client):  # специальная встроенная фикстура, которая умеет делать запросы
    response = client.get("/")  # get запрос на корневой урл
    assert response.status_code == 404  # так как нет такой страницы должен вернутся статус 404 (not found)
