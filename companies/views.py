from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from companies.models import Company


@method_decorator(csrf_exempt, name='dispatch')  # возвращаем метод декоратор для отключения
class CompanyImageView(UpdateView):  # класс наследуется от родительского класса UpdateView
    model = Company  # обязательный модуль, который указывает название используемой модели
    fields = ['name', 'logo']  # указываем поля модели для того, чтоб CreateView
    # сгенерировал автоматически в м-формочку

    def post(self, request, *args, **kwargs):  # с обязательными аргументами args и kwargs
        self.object = self.get_object()

        self.object.logo = request.FILES['logo']  # в request.FILES лежат все файла, которые послал пользователь
        self.object.save()

        return JsonResponse({
            'id': self.object.id,
            'name': self.object.name,
            'logo': self.object.logo.url if self.object.logo else None,
        })
