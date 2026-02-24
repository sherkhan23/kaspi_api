from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения")

    class Meta:
        abstract = True


class Users(CreatedModel):
    telegram_id = models.BigIntegerField(
        verbose_name='Telegram ID',
        help_text='Telegram ID'
    )
    send = models.BooleanField(
        default=False
    )


class Referral(models.Model):
    telegram_id = models.BigIntegerField(
        verbose_name='Telegram ID'
    )

    name = models.CharField(
        null=True,
        max_length=5000
    )

    amount = models.IntegerField(
        null=True,
        verbose_name='Кол-во приглашенных'
    )


class Account(models.Model):
    telegram_id = models.BigIntegerField(
        null=True,
        verbose_name='Telegram ID'
    )

    account = models.CharField(
        verbose_name='Phone',
        null=True,
        max_length=5000
    )

    sb_id = models.CharField(
        verbose_name='SB ID',
        null=True,
        max_length=5000
    )

    sum = models.IntegerField(
        null=True,
        verbose_name='Сумма'
    )

    name = models.CharField(
        null=True,
        verbose_name='Имя для Тильды',
        max_length=5000
    )

    payment_title = models.CharField(
        null=True,
        verbose_name='Назначение платежа',
        max_length=5000
    )

    phone = models.CharField(
        null=True,
        max_length=5000,
        verbose_name='Номер для тильды'
    )

    email = models.CharField(
        null=True,
        max_length=5000,
        verbose_name='Email для тильды'
    )


    kaspi_order_id = models.CharField(
        null=True,
        max_length=5000,
        verbose_name='ID заказа для Каспи'
    )

class Transaction(models.Model):
    txn_id = models.CharField(max_length=18, unique=True)
    prv_txn = models.CharField(max_length=20, blank=True, null=True)
    account = models.CharField(max_length=200)
    command = models.CharField(max_length=10)
    txn_date = models.DateTimeField(blank=True, null=True)
    sum = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    result = models.IntegerField(default=0)
    comment = models.TextField(blank=True, null=True)
