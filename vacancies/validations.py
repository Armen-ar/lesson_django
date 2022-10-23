from rest_framework import serializers


class NotInStatusValidator:
    def __init__(self, statuses):
        if not isinstance(statuses, list):  # если статусы не список
            statuses = [statuses]  # превратить в список
        self.statuses = statuses

    def __call__(self, value):
        if value in self.statuses:
            raise serializers.ValidationError('Incorrect status.')
