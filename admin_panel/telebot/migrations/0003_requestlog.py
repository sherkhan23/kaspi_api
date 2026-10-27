from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telebot', '0002_account_kaspi_order_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('INFO', 'Info'), ('WARNING', 'Warning'), ('ERROR', 'Error'), ('SUCCESS', 'Success')], default='INFO', max_length=20, verbose_name='Уровень')),
                ('endpoint', models.CharField(blank=True, default='', max_length=100, verbose_name='Эндпоинт')),
                ('message', models.CharField(max_length=500, verbose_name='Сообщение')),
                ('details', models.TextField(blank=True, null=True, verbose_name='Детали')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата')),
            ],
            options={
                'verbose_name': 'Лог',
                'verbose_name_plural': 'Логи',
                'ordering': ['-created_at'],
            },
        ),
    ]
