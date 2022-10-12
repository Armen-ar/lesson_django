from rest_framework import serializers

from vacancies.models import Vacancy, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class VacancyListSerializer(serializers.ModelSerializer):
    username = serializers.CharField()  # можем добавлять поля к модели, которых нет
    skills = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )  # добавим связь модели vacancy и модели skills в поле skills (SlugRelatedField) и ему нужно указать

    # many (всё из списка), read_only (потому что менять его нельзя) и slug_field поле, на которое будем ссылаться

    # id = serializers.IntegerField()
    # text = serializers.CharField(max_length=2000)
    # slug = serializers.CharField(max_length=50)
    # status = serializers.CharField(max_length=6)
    # created = serializers.DateField()
    # username = serializers.CharField(max_length=100)
    class Meta:
        model = Vacancy
        fields = ['id', 'text', 'slug', 'status', 'created', 'username', 'skills']


class VacancyDetailSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Vacancy
        fields = '__all__'  # все поля отобразятся, поле user и поле skills первичными ключами


class VacancyCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # по умолчанию берётся из модели, но говорим что необязательно
    skills = serializers.SlugRelatedField(  # для того, чтоб принимать поле от метода is_valid ниже допишем поле
        required=False,  # необязательно
        many=True,  # их много
        queryset=Skill.objects.all(),  # значения этого поля будут из queryset....
        slug_field='name'  # название поля, откуда берётся значение
    )

    class Meta:
        model = Vacancy
        fields = '__all__'  # все поля отобразятся

    """метод вытаскивает все skills, прячет их от валидатора, а затем даёт пройтись по ним самостоятельно"""

    def is_valid(self, *, raise_exception=False):
        self._skills = self.initial_data.pop('skills', [])  # из тех данных, которые прислал пользователь
        # self.initial_data выбирает по ключу 'skills' значение и засовываем его во внутренний словарь self._skills
        # и по умолчанию пустой список
        return super().is_valid(raise_exception=raise_exception)

    def create(self, validated_data):  # принимает отвалидированные(точные) данные
        vacancy = Vacancy.objects.create(**validated_data)

        for skill in self._skills:
            skill_obj, _ = Skill.objects.get_or_create(  # _ вместо create (андерскор) это мусорная корзина, куда
                # кладём ненужные данные, но обязаны их достать
                name=skill
            )  # берём скилл-объект и дату создания из модели Skill. У него вызываем метод objects и у него
            # вызываем метод get_or_create (запрос или, если нет, создание), в который передаём поле.
            vacancy.skills.add(skill_obj)  # в вакансию кладёт skill_obj
        vacancy.save()  # сохраняем

        return vacancy  # возвращает вакансию


class VacancyUpdateSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(  # для того, чтоб принимать поле от метода is_valid ниже допишем поле
        required=False,  # необязательно
        many=True,  # их много
        queryset=Skill.objects.all(),  # значения этого поля будут из queryset....
        slug_field='name'  # название поля, откуда берётся значение
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # менять его нельзя
    created = serializers.DateField(read_only=True)  # менять его нельзя

    class Meta:
        model = Vacancy
        fields = ['id', 'text', 'status', 'slug', 'user', 'created', 'skills']  # поля, которые отобразятся

    """метод вытаскивает все skills, прячет их от валидатора, а затем даёт пройтись по ним самостоятельно"""

    def is_valid(self, *, raise_exception=False):
        self._skills = self.initial_data.pop('skills', [])  # из тех данных, которые прислал пользователь
        # self.initial_data выбирает по ключу 'skills' значение и засовываем его во внутренний словарь self._skills
        # и по умолчанию пустой список
        return super().is_valid(raise_exception=raise_exception)

    def save(self, **kwargs):  # метод сохранения
        vacancy = super().save()

        for skill in self._skills:
            skill_obj, _ = Skill.objects.get_or_create(  # _ вместо create (андерскор) это мусорная корзина, куда
                # кладём ненужные данные, но обязаны их достать
                name=skill
            )  # берём скилл-объект и дату создания из модели Skill. У него вызываем метод objects и у него
            # вызываем метод get_or_create (запрос или, если нет, создание), в который передаём поле.
            vacancy.skills.add(skill_obj)  # в вакансию кладёт skill_obj
        vacancy.save()  # сохраняем

        return vacancy  # возвращает вакансию


class VacancyDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ['id']  # поле, которое отобразится
