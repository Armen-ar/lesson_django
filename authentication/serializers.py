from rest_framework import serializers

from authentication.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = super().create(validated_data)  # сохраняем пользователя передав в метод валидные данные

        user.set_password(user.password)  # вызываем у сохранённого пользователя метод set_password,
        # который захеширует пароль
        user.save()  # сохраняем

        return user


