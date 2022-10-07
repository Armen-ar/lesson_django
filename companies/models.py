from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=20)
    logo = models.ImageField(upload_to='logos/')  # картинки и положить их (путь до директории) папка logos

    class Meta:
        verbose_name = 'Компания'  # как будем называть нашу модель в единственном числе
        verbose_name_plural = 'Компании'  # как будем называть нашу модель во множественном числе
