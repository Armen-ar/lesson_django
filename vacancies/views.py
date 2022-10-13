from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q, F
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from amazing_hunting import settings
from authentication.models import User
from vacancies.models import Vacancy, Skill
from vacancies.permissions import VacancyCreatePermission
from vacancies.serializers import VacancyListSerializer, VacancyDetailSerializer, VacancyCreateSerializer, \
    VacancyUpdateSerializer, VacancyDestroySerializer, SkillSerializer

"""Стало так"""


def hello(request):
    return HttpResponse('Hello World')


class SkillsViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class VacancyListView(ListAPIView):  # для род. класс на ListAPIView нужно указать обязательные атрибуты
    queryset = Vacancy.objects.all()  # список всех записей модели
    serializer_class = VacancyListSerializer  # из сериализации список вакансий

    def get(self, request, *args, **kwargs):
        vacancy_text = request.GET.get('text')  # в переменной будем хранить текст, который берём из
        # reques(запроса) у него вызываем метод GET, у которого вызываем метод get и передаём туда
        # ключ (text). По умолчанию None.
        if vacancy_text:  # если получили текст
            self.queryset = self.queryset.filter(
                text__icontains=vacancy_text  # по вхождению, но без учёта регистра (буква i перед contains)
            )  # переопределяем queryset в запросе через фильтр

        # skill_name = request.GET.get('skill')  # в переменной будем хранить навык, который берём из
        # # reques(запроса) у него вызываем метод GET, у которого вызываем метод get и передаём туда
        # # ключ (skill). По умолчанию None.
        """вместо кода выше для поиска по нескольким skill-ам"""
        skills = request.GET.getlist('skill')  # в переменной будем хранить список навыков(getlist)
        skill_q = None
        # if skill_name:  # если получили навык
        #     self.queryset = self.queryset.filter(
        #         skills__name__contains=skill_name  # указываем таблицу(skill), поле в этой таблице(name) и лукап
        #     )  # переопределяем queryset в запросе через фильтр
        """вместо кода выше для поиска по нескольким skill-ам"""
        for skill in skills:
            if skill_q is None:  # если skill_q ещё пустой, то добавим условие фильтрации
                skill_q = Q(skills__name__contains=skill)  # Q класс - это служебный класс для сбора условий фильтраций
            else:
                skill_q |= Q(skills__name__contains=skill)  # если в Q что-то есть, то добавим через логическое
                # или '|' ещё один класс с условием
        if skill_q:
            self.queryset = self.queryset.filter(skill_q)
        return super().get(request, *args, **kwargs)  # возвращает родительский метод, а остальное делает DRF


class VacancyDetailView(RetrieveAPIView):  # для детального вывода нужно указать обязательные атрибуты
    queryset = Vacancy.objects.all()  # список всех записей модели
    serializer_class = VacancyDetailSerializer  # из сериализации конкретная вакансия
    permission_classes = [IsAuthenticated]  # авторизация для детального просмотра вакансий(список с пермишами-доступом)


"""декораторы не нужны, т.к. CreateAPIView уже работает как API"""


class VacancyCreateView(CreateAPIView):
    queryset = Vacancy.objects.all()  # список всех записей модели
    serializer_class = VacancyCreateSerializer  # из сериализации добавление вакансии
    permission_classes = [IsAuthenticated, VacancyCreatePermission]  # сначала проверяет на аутентификацию пользователя


class VacancyUpdateView(UpdateAPIView):  # класс наследуется от родительского класса CreateView
    queryset = Vacancy.objects.all()  # список всех записей модели
    serializer_class = VacancyUpdateSerializer  # из сериализации обновления вакансии


class VacancyDeleteView(DestroyAPIView):
    queryset = Vacancy.objects.all()  # список всех записей модели
    serializer_class = VacancyDestroySerializer  # из сериализации удаления вакансии


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_vacancies(request):
    user_qs = User.objects.annotate(vacancies=Count('vacancy'))  # у модели User вызываем метод objects и чтоб
    # сгруппировать данные у него вызываем метод annotate (он добавляет к записи дополнительную колонку,
    # которую кладёт что он сделал). Вместо Count может быть Max, Min и т.д.

    paginator = Paginator(user_qs, settings.TOTAL_ON_PAGE)  # переменная это объект класса Paginator,
    # в которую передаём аргумент сгруппированные данные и константу, дописанную в setting.py
    page_number = request.GET.get('page', 1)  # это номер страницы, который передал пользователь
    # по умолчанию 1 стр.
    page_object = paginator.get_page(page_number)  # у пагинатора вызываем метод get_page и туда передаём номер

    users = []  # пустой список пользователей
    for user in page_object:
        users.append({
            'id': user.id,
            'name': user.username,
            'vacancies': user.vacancies
        })

    response = {
        'items': users,
        'num_pages': paginator.num_pages,
        'total': paginator.count,
        'avg': user_qs.aggregate(avg=Avg('vacancies'))['avg']  # выводит среднее значение по колонке
    }

    return JsonResponse(response)


class VacancyLikeView(UpdateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDetailSerializer

    def put(self, request, *args, **kwargs):
        Vacancy.objects.filter(pk__in=request.data).update(likes=F('likes') + 1)  # у вакансии вызываем метод objects
        # и фильтруем по первичным ключам и у этого всего вызываем метод обновления(update) поля like обновлять на один
        # и класс F('likes') говорит о том что это поле текущей записи(берёт текущее значение и увеличивает его на один)
        return JsonResponse(
            VacancyDetailSerializer(Vacancy.objects.filter(pk__in=request.data), many=True).data, safe=False
        )
        # возвращает отфильтрованные данные в виде json(.data)


"""Было так"""
# # # функции
# # #########
# # @csrf_exempt  # декоратор говорит о том, что здесь проверять csrf-токен не надо
# # def index(request):
# #     if request.method == "GET":  # если это запрос должны собрать все вакансии
# #         vacancies = Vacancy.objects.all()  # objects это ОРМ, но в целом это менеджер всё из БД
# #         search_text = request.GET.get('text', None)  # вытаскиваем текст из запроса, если нет передаёт None
# #         if search_text:  # если есть текст
# #             vacancies = vacancies.filter(text=search_text)
# #
# #         response = []  # пустой список для получения данных в json формате
# #         for vacancy in vacancies:
# #             response.append({
# #                 "id": vacancy.id,
# #                 "text": vacancy.text
# #             })
# #
# #         return JsonResponse(
# #             response,
# #             safe=False,
# #             json_dumps_params={
# #                 "ensure_ascii": False
# #             })
# #         # возвращает полноценный json, safe=False говорит, что там не словарь (отключи проверки)
# #         # и json_dumps_params это работа json с кириллицей, но это писать не надо для фронта, а
# #         # для получения русского алфавита без этой записи можно пользоваться Postman запросы.
# #
# #     elif request.method == "POST":  # если метод пост, то мы сами будем сохранять данные
# #         vacancy_data = json.loads(request.body)  # переменная хранит тело(body)запроса(request) в виде json
# #
# #         vacancy = Vacancy()  # получая объект
# #         vacancy.text = vacancy_data['text']  # сохраняем в объекте по полю text текст из POST, а id autoincrement
# #
# #         vacancy.save()  # сохраняем объект (метод save вызывает 'вставлять' на базу данных)
# #
# #         return JsonResponse({
# #             "id": vacancy.id,
# #             "text": vacancy.text
# #         })  # возвращает то, что сохранили
# #
# #
# # # классы
# # #########
# # @method_decorator(csrf_exempt, name='dispatch')  # декоратор, который принимает аргументом декоратор(говорит о том, что
# # # здесь проверять csrf-токен не надо) и атрибут name (отправлять)
# # class VacancyView(View):
# #     def get(self, request):
# #         vacancies = Vacancy.objects.all()  # objects это ОРМ, но в целом это менеджер всё из БД
# #         search_text = request.GET.get('text', None)  # вытаскиваем текст из запроса, если нет передаёт None
# #         if search_text:  # если есть текст
# #             vacancies = vacancies.filter(text=search_text)
# #
# #         response = []  # пустой список для получения данных в json формате
# #         for vacancy in vacancies:
# #             response.append({
# #                 "id": vacancy.id,
# #                 "text": vacancy.text
# #             })
# #
# #         return JsonResponse(
# #             response,
# #             safe=False,
# #             json_dumps_params={
# #                 "ensure_ascii": False
# #             })
# #         # возвращает полноценный json, safe=False говорит, что там не словарь (отключи проверки)
# #         # и json_dumps_params это работа json с кириллицей, но это писать не надо для фронта, а
# #         # для получения русского алфавита без этой записи можно пользоваться Postman запросы.
# #
# #     def post(self, request):
# #         vacancy_data = json.loads(request.body)  # переменная хранит тело(body)запроса(request) в виде json
# #
# #         vacancy = Vacancy()  # получая объект
# #         vacancy.text = vacancy_data['text']  # сохраняем в объекте по полю text текст из POST, а id autoincrement
# #
# #         vacancy.save()  # сохраняем объект (метод save вызывает 'вставлять' на базу данных)
# #
# #         return JsonResponse({
# #             "id": vacancy.id,
# #             "text": vacancy.text
# #         })  # возвращает то, что сохранили
#
# """Стало так"""
#
# """Было так"""
# class VacancyListView(ListView):  # меняем родительский класс View на ListView и для этого нужно
#     # указать обязательный атрибут model
#     model = Vacancy
#
#     def get(self, request, *args, **kwargs):  # добавить аргументы arg и kwargs
#         super().get(request, *args, **kwargs)  # вызываем супер с аргументами и теперь у self появится
#         # атрибут object_list (116 строка), в котором будут все наши вакансии
#
#         search_text = request.GET.get('text', None)  # вытаскиваем текст из запроса, если нет передаёт None
#         if search_text:  # если есть текст
#             self.object_list = self.object_list.filter(text=search_text)
#
#             # total = self.object_list.count()  # переменная хранит количество всех вакансий
#             # page_number = int(request.GET.get('page', 1))  # это номер страницы строкой (забираем его из request.GET
#             # # выбранное поле 'page'-страницу) и поэтому сворачиваем в int (число), который передал пользователь,
#             # # а если нет этой страницы по умолчанию 1 стр.
#             # offset = (page_number - 1) * settings.TOTAL_ON_PAGE  # отступ на сколько отступаем сначала, чтобы вытащить
#             # # следующую страницу, т.е. для первой стр. отступ 0, для второй - 10, для третьей 20 и т.д.
#             # if offset < total:
#             #     self.object_list = self.object_list[offset:offset + settings.TOTAL_ON_PAGE]  # выводит с отступом т.е.
#             #     # с какого по какой
#             # else:
#             #     self.object_list = self.object_list[offset:offset + total]  # иначе выводи с отступ. с какого до конца
#             """Вместо всего этого используется встроенная в Django классы после сортировки"""
#
#         self.object_list = self.object_list.select_related('user').prefetch_related('skills').order_by('-text')  # все
#         # вакансии равны вакансии вызываем метод select_related('user'), который сделает 'JOIN'(.....)
#         # вызываем метод prefetch_related('skill'), который имитирует JOIN для MANY2MANY таблиц (запоминает все skill,
#         # вытащит их отдельным запросом, затем пересоберёт в нужный формат Python)
#         # и у него вызываем метод order_by, в которую передаём сортируемое поле '-' в обратном порядке.
#
#         """пагинация"""
#         paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)  # переменная это объект класса Paginator,
#         # в которую передаём аргумент все вакансии и константу, дописанную в setting.py
#         page_number = request.GET.get('page', 1)  # это номер страницы, который передал пользователь
#         # по умолчанию 1 стр.
#         page_object = paginator.get_page(page_number)  # у пагинатора вызываем метод get_page и туда передаём номер
#
#         # vacancies = []  # пустой список для получения данных в json формате
#         # for vacancy in page_object:
#         #     vacancies.append({
#         #         "id": vacancy.id,
#         #         "slug": vacancy.slug,
#         #         "text": vacancy.text,
#         #         "status": vacancy.status,
#         #         "created": vacancy.created,
#         #         "username": vacancy.user.username,
#         #         "skills": list(map(str, vacancy.skills.all()))  # все записи в скилов из вакансии, применяем
#         #         # к каждому метод str (map применение функции к каждому) и всё это в виде списка
#         #     })
#         """т.к. у объекта нет поля username (мы получали его через поле user) пишем следующую строку"""
#         list(map(lambda x: setattr(x, "username", x.user.username if x.user else None), page_object))
#         # map (на каждый элемент (объект) применима функция), setattr(метод, который к нашему объекту добавляет
#         # атрибут), (x - это объект, "username" - какой атрибут добавить, x.user.username - от объекта какое поле
#         # добавить), но не у каждого user есть username поэтому допишем page_object - к какому объекту всё это
#         # применить и всё это привести в вид списка - list
#
#         response = {
#             'items': VacancyListSerializer(page_object, many=True).data,  # page_object (объект на странице), в котором
#             # лежит список вакансий и заметить, что их много (many=True) т.к. по умолчанию сериализатор принимает
#             # один объект (сериализатору нужно обработать список объектов) и у сериализатора нужно вызвать метод data,
#             # чтобы получить у него json.
#             'num_pages': paginator.num_pages,
#             'total': paginator.count,
#         }
#
#         return JsonResponse(
#             response,
#             safe=False,
#             json_dumps_params={
#                 "ensure_ascii": False
#             })
#         # возвращает полноценный json, safe=False говорит, что там не словарь (отключи проверки)
#         # и json_dumps_params это работа json с кириллицей, но это писать не надо для фронта, а
#         # для получения русского алфавита без этой записи можно пользоваться Postman запросы.
#
#
# # # функции
# # #########
# # def get(request, vacancy_id):
# #     if request.method == "GET":
# #         try:
# #             vacancy = Vacancy.objects.get(pk=vacancy_id)  # первичный ключ pk
# #         except Vacancy.DoesNotExist:
# #             return JsonResponse({"error": "Not found"}, status=404)  # status 404 - запись не была найдена
# #
# #         return JsonResponse({
# #             "id": vacancy.id,
# #             "text": vacancy.text
# #         },
# #             json_dumps_params={
# #                 "ensure_ascii": False
# #             })
# #
# # # классы
# # #########
# # class VacansyDetailView(DetailView):  # класс детального вывода, который наследуется от класса DetailView
# #     model = Vacancy  # обязательный модуль, который указывает название используемой модели
# #
# #     def get(self, request, *args, **kwargs):
# #         vacancy = self.get_object()  # метод вернёт наш элемент
# #
# #         return JsonResponse({
# #             "id": vacancy.id,
# #             "text": vacancy.text
# #         })
# # после вывода всех логично вывод детально (по id)
#
#
# """Стало так"""
#
# # классы
# ########
#
#
# class VacancyDetailView(DetailView):  # класс детального вывода, который наследуется от класса DetailView
#     model = Vacancy  # обязательный модуль, который указывает название используемой модели
#
#     def get(self, request, *args, **kwargs):
#         vacancy = self.get_object()  # метод вернёт наш элемент
#         # После сериализации не нужно
#         # return JsonResponse({
#         #     "id": vacancy.id,
#         #     "slug": vacancy.slug,
#         #     "text": vacancy.text,
#         #     "status": vacancy.status,
#         #     "created": vacancy.created,
#         #     "user": vacancy.user_id,
#         #     "skills": list(map(str, vacancy.skills.all()))  # все записи в скилов из вакансии, применяем
#         #         # к каждому метод str (map применение функции к каждому) и всё это в виде списка
#         # })
#
#         return JsonResponse(VacancyDetailSerializer(vacancy).data)  # передаём в сериализатор элемент vacancy
#         # и превратить всё это в json (.data)
#
#
# """Было так"""
# # функция
# #########
# # def post(self, request):
# #     vacancy_data = json.loads(request.body)  # переменная хранит тело(body)запроса(request) в виде json
# #
# #     vacancy = Vacancy()  # получая объект
# #     vacancy.text = vacancy_data['text']  # сохраняем в объекте по полю text текст из POST, а id autoincrement
# #
# #     vacancy.save()  # сохраняем объект (метод save вызывает 'вставлять' на базу данных)
# #
# #     return JsonResponse({
# #         "id": vacancy.id,
# #         "text": vacancy.text
# #     })  # возвращает то, что сохранили
#
#
# """Стало так"""
#
#
# # классы
# ########
#
#
# @method_decorator(csrf_exempt, name='dispatch')  # возвращаем метод декоратор для отключения
# # проверки и работы с ним как с API
# class VacancyCreateView(CreateView):  # класс наследуется от родительского класса CreateView
#     model = Vacancy  # обязательный модуль, который указывает название используемой модели
#     fields = ['slug', 'text', 'status', 'created', 'user', 'skills']  # указываем поля модели для того,
#     # чтоб CreateView сгенерировал автоматически в м-формочку
#
#     def post(self, request, *args, **kwargs):  # добавляем обязательные аргументы args и kwargs
#         # vacancy_data = json.loads(request.body)  # переменная хранит тело(body)запроса(request) в виде json
#         """используя сериализатор пишем, т.к. она преврашщает в json и обратно"""
#         vacancy_data = VacancyCreateSerializer(data=json.loads(request.body))  # превратив в json передаёт в сериализа.
#         if vacancy_data.is_valid():  # проверив все данные (пришли в тех форматах и ограничениях, которые указали)
#             # и из сериализатора вызвать save
#             vacancy_data.save()  # сохраняем
#         else:
#             return vacancy_data.errors  # иначе вернуть ошибки из данных
#         # # Это всё можно не писать вместо этого выше 5 строк
#         # vacancy = Vacancy.objects.create(
#         #     slug=vacancy_data['slug'],
#         #     text=vacancy_data['text'],
#         #     status=vacancy_data['status'],
#         # )  # получая объект, вызывая у него objects, а у него метод create, который принимает список полей
#         #
#         # vacancy.user = get_object_or_404(User, pk=vacancy_data['user_id'])  # переменная сохраняет метод,
#         # # (в который передаём объект из модели User по pk равному id пользователя) и который возвращает либо объект,
#         # # либо ошибку 404
#         #
#         # for skill in vacancy_data['skills']:  # пройдя по списку skills в отправленных данных vacancy_data
#         #     # try:
#         #     #     skill_obj = Skill.objects.get(name=skill)
#         #     # except Skill.DoesNotExist:
#         #     #     # return JsonResponse({'error': 'Skill not found'}, status=404)  # если не найден выведет ошибку
#         #     #     """вместо вывода ошибки пишем нижеследующее"""
#         #     #     skill_obj = Skill.objects.create(name=skill)
#         #     """вместо строк выше для обработки ошибки 404, пишем следующее:"""
#         #     skill_obj, created = Skill.objects.get_or_create(
#         #         name=skill,
#         #         defaults={
#         #             "is_activ": True
#         #         }
#         #     )  # берём скилл_объект и дату создания из модели Skill. У него вызываем метод objects и у него
#         #     # вызываем метод get_or_create, в который передаём поле. Поле по которому хотим достать и указываем
#         #     # значение по умолчанию defaults словарик. При get запросе по name=skill и если не найдёт, то создаёт
#         #     # новый skill с именен is_activ и полем True
#         #     vacancy.skills.add(skill_obj)  # если есть выводит объект
#         # vacancy.save()  # сохранение после добавления
#         #
#         # return JsonResponse({
#         #     "id": vacancy.id,
#         #     "slug": vacancy.slug,
#         #     "text": vacancy.text,
#         #     "status": vacancy.status,
#         #     "created": vacancy.created,
#         #     "user": vacancy.user_id,
#         # })  # возвращает то, что сохранили
#
#         return JsonResponse(vacancy_data.data)
#
#
# """Добавляем методы update-редактирование и delete-удалять"""
#
#
# @method_decorator(csrf_exempt, name='dispatch')  # возвращаем метод декоратор для отключения
# # проверки и работы с ним как с API
# class VacancyUpdateView(UpdateView):  # класс наследуется от родительского класса CreateView
#     model = Vacancy  # обязательный модуль, который указывает название используемой модели
#     fields = ['slug', 'text', 'status', 'skills']  # указываем поля модели для того,
#
#     # чтоб CreateView сгенерировал автоматически в м-формочку кроме пользователя user и created
#
#     def patch(self, request, *args, **kwargs):  # добавляем обязательные аргументы args и kwargs
#         super().post(request, *args, **kwargs)  # вызываем у супера метод post с аргументами
#
#         vacancy_data = json.loads(request.body)  # переменная хранит тело(body)запроса(request) в виде json
#         self.object.slug = vacancy_data['slug']  # вызывая у self метод object и переписываем определённое поле
#         self.object.text = vacancy_data['text']
#         self.object.status = vacancy_data['status']
#
#         for skill in vacancy_data['skills']:  # пройдя по списку skills в отправленных данных vacancy_data
#             try:
#                 skill_obj = Skill.objects.get(name=skill)
#             except Skill.DoesNotExist:
#                 return JsonResponse({'error': 'Skill not found'}, status=404)  # если не найден выведет строку об ошибке
#             self.object.skills.add(skill_obj)  # если есть выводит объект
#
#         self.object.save()  # для сохранения данных в БД вызываем метод save у object
#
#         return JsonResponse({
#             "id": self.object.id,
#             "slug": self.object.slug,
#             "text": self.object.text,
#             "status": self.object.status,
#             "created": self.object.created,
#             "user": self.object.user_id,
#             "skills": list(map(str, self.object.skills.all()))  # все записи в скилов из вакансии, применяем
#                 # к каждому метод str (map применение функции к каждому) и всё это в виде списка
#         })  # возвращает то, что сохранили
#
#
# @method_decorator(csrf_exempt, name='dispatch')  # возвращаем метод декоратор для отключения
# # проверки и работы с ним как с API
# class VacancyDeleteView(DeleteView):
#     model = Vacancy  # обязательный модуль, который указывает название используемой модели
#     success_url = "/"  # url на которую нужно направить пользователя, после того, как удалили запись(пока просто "/")
#
#     def delete(self, request, *args, **kwargs):  # c обязательными аргументами
#         super().delete(request, *args, **kwargs)  # вызываем у супера метод делит с аргументами
#
#         return JsonResponse({'status': 'ok'}, status=200)
#
#
# class UserVacancyDetailView(View):
#     def get(self, request):
#         user_qs = User.objects.annotate(vacancies=Count('vacancy'))  # у модели User вызываем метод objects и чтоб
#         # сгруппировать данные у него вызываем метод annotate (он добавляет к записи дополнительную колонку,
#         # которую кладёт что он сделал). Вместо Count может быть Max, Min и т.д.
#
#         paginator = Paginator(user_qs, settings.TOTAL_ON_PAGE)  # переменная это объект класса Paginator,
#         # в которую передаём аргумент сгруппированные данные и константу, дописанную в setting.py
#         page_number = request.GET.get('page', 1)  # это номер страницы, который передал пользователь
#         # по умолчанию 1 стр.
#         page_object = paginator.get_page(page_number)  # у пагинатора вызываем метод get_page и туда передаём номер
#
#         users = []  # пустой список пользователей
#         for user in page_object:
#             users.append({
#                 'id': user.id,
#                 'name': user.username,
#                 'vacancies': user.vacancies
#             })
#
#         response = {
#             'items': users,
#             'num_pages': paginator.num_pages,
#             'total': paginator.count,
#             'avg': user_qs.aggregate(avg=Avg('vacancies'))['avg']  # выводит среднее значение по колонке
#         }
#
#         return JsonResponse(response)
