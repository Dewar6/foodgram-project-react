from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        verbose_name='Логин пользователя',
        help_text='Укажите логин',
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[validate_username, ]
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        help_text='Укажите имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        help_text='Укажите фамилию',
        max_length=150,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        help_text='Укажите адрес электронной почты',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user',
            )
        ]

    def __str__(self):
        return self.username


class UserSubscribe(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        unique_together = ['subscriber', 'target_user']

    def __str__(self):
        return f'{self.subscriber} подписан на {self.target_user}'