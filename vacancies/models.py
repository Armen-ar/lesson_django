from django.db import models

from authentication.models import User


class Skill(models.Model):
    name = models.CharField(max_length=20)
    is_activ = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Навык'  # как будем называть нашу модель в единственном числе
        verbose_name_plural = 'Навыки'  # как будем называть нашу модель во множественном числе

    def __str__(self):
        return self.name  # в панели админа будет выводить вместо name то, что записано будет в name


class Vacancy(models.Model):
    STATUS = [
        ("draft", "Черновик"),
        ("open", "Открыта"),
        ("closed", "Закрыта"),
    ]  # константа (список) из таплов, где первое значение это то, что будет лежать в БД, а второе это
    # человекочитаемое значение, которое отобразится пользователю не из вне, а из админки
    slug = models.SlugField(max_length=50)
    text = models.CharField(max_length=2000)
    status = models.CharField(max_length=6, choices=STATUS, default="draft")  # исходя из количества символов в самой
    # длинной строке 'closed' и 'choices' это выбирать из списка константы и по умолчанию 'draft' т.е. будут
    # создаваться со статусом Черновик
    created = models.DateField(auto_now_add=True)  # дата создания, атрибут 'auto_now_add'(поставь текущее значение в
    # момент создания)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # обязательный атрибут модель User и при
    # удалении записи User каскадом удалить записи models.CASCADE
    skills = models.ManyToManyField(Skill)

    likes = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Вакансия'  # как будем называть нашу модель в единственном числе
        verbose_name_plural = 'Вакансии'  # как будем называть нашу модель во множественном числе
        # ordering = ['text', 'slug']  # сортировка по полю (не рекомендуется) можно несколько

    def __str__(self):
        return self.slug  # в панели админа будет выводить вместо slug то, что записано будет в slug

    @property  # этот декоратор позволяет чтобы этот метод вёл себя как атрибут (поле класса)
    def username(self):
        return self.user.username if self.user else None
