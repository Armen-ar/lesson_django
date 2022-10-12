from rest_framework.permissions import BasePermission

from authentication.models import User


class VacancyCreatePermission(BasePermission):
    massage = "Adding vacancies for non hr user not allowed."  # Добавление вакансий для не hr пользователя запрещено

    def has_permission(self, request, view):
        if request.user.role == User.HR:
            return True
        return False
