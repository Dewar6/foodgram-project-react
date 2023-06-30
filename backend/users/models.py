from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.validators import validate_username


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin'
        USER = 'user'

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
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        help_text='Укажите фамилию',
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        help_text='Укажите адрес электронной почты',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    role = models.CharField(
        verbose_name='Статус пользователя',
        max_length=50,
        choices=Role.choices,
        default=Role.USER,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('Разрешения пользователя'),
        blank=True,
        help_text=_('Выберите разрешения пользователя.'),
        related_name='users_with_permission'
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('Группы пользователя'),
        blank=True,
        help_text=_('Выберите группы, к которым принадлежит пользователь.'),
        related_name='users_in_group'
    )
    password = models.CharField(
        verbose_name='Пароль',
        help_text='Введите пароль',
        max_length=128,
        blank=False,
        null=False
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