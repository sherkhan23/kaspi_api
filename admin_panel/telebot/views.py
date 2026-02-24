import logging
import re
from datetime import datetime
from urllib.parse import parse_qs

from django.http import JsonResponse, HttpResponse

import requests
from django.views.decorators.csrf import csrf_exempt
import json

from admin_panel.telebot.models import Account, Transaction
from decimal import *


@csrf_exempt
def create_tilda(request):
    return JsonResponse({'status': 'ok'}, status=200)
    # try:
    #     raw_data = request.body.decode('utf-8')  # Декодируем байтовую строку в текст
    #     parsed_data = parse_qs(raw_data)  # Парсим URL-кодированную строку в словарь
    #
    #     # Преобразуем значения из списка в обычные строки (берем первый элемент)
    #     cleaned_data = {key: value[0] if len(value) == 1 else value for key, value in parsed_data.items()}
    #
    #     if "Phone" in cleaned_data:
    #         phone_raw = cleaned_data["Phone"]
    #         phone_digits = re.sub(r"\D", "", phone_raw)  # Удаляем всё, кроме цифр
    #         if phone_digits.startswith("8"):  # Если номер начинается с 8, заменяем на 7
    #             phone_digits = "7" + phone_digits[1:]
    #         elif phone_digits.startswith("7"):
    #             phone_digits = "7" + phone_digits[1:]
    #         cleaned_data["Phone"] = phone_digits  # Убираем "+"
    #
    #     # Логируем обработанные данные для проверки
    #     logging.warning(json.dumps(cleaned_data, indent=4, ensure_ascii=False))
    #
    #     Account.objects.create(
    #         phone=cleaned_data["Phone"],
    #         name=cleaned_data["Name"],
    #         sum=cleaned_data["sum"],
    #         email=cleaned_data["Email"],
    #         payment_title=cleaned_data["payment_title"],
    #     )
    #     send_request_kaspi_tilda(cleaned_data["Phone"], amount=cleaned_data["sum"], client_id=cleaned_data["Phone"])
    #     return JsonResponse({'status': True, 'message': 'Аккаунт успешно создан!',
    #                          'data': [
    #                              {'name': cleaned_data["Name"], 'phone': cleaned_data["Phone"],
    #                               'sum': cleaned_data["sum"],
    #                               'email': cleaned_data["Email"]}]}, status=200)
    # except Exception as e:
    #     logging.warning(e)
    #     return JsonResponse({'status': True, 'message': 'Привязано успешно!'}, status=200)

@csrf_exempt
def create_account(request):
    try:
        if request.method == 'POST':
            logging.warning(request.body)
            data = json.loads(request.body)
            logging.warning(data)
            if 't_pay' in data.keys():
                logging.warning('+++')
                name = data.get('Name')
                if "Phone" in data:
                    phone_raw = data["Phone"]
                    phone_digits = re.sub(r"\D", "", phone_raw)  # Удаляем всё, кроме цифр
                    if phone_digits.startswith("8"):  # Если номер начинается с 8, заменяем на 7
                        phone_digits = "7" + phone_digits[1:]
                    elif phone_digits.startswith("7"):
                        phone_digits = "7" + phone_digits[1:]
                    data["phone"] = phone_digits  # Убираем "+"
                sum = data.get('sum') if 'sum' in data.keys() else None
                email = data.get('Email')
                payment_title = data.get('payment_title') if 'payment_title' in data.keys() else None
                order_id = data.get('order_id') if 'order_id' in data.keys() else None

                Account.objects.create(
                    phone=data['Phone'],
                    name=name,
                    sum=sum,
                    email=email,
                    payment_title=payment_title,
                    kaspi_order_id=data['Phone']
                )
                logging.warning('СОЗДАЛИ АККАУНТ ТИЛЬДА')
                req_data = send_request_kaspi_tilda(data['phone'], amount=sum, client_id=data['Phone'])
                logging.warning('REQ DATA')
                logging.warning(req_data)
                return JsonResponse({'status': True, 'message': 'Аккаунт успешно создан!',
                                     'data': [
                                         {'name': name, 'phone': data['Phone'], 'sum': sum, 'email': email,
                                          "payment_title": payment_title}]})
            else:
                telegram_id = data.get('telegram_id')
                sb_id = data.get('sb_id')
                account = data.get('account')
                sum = data.get('sum')
                name = data.get('name') if 'name' in data.keys() else None
                payment_title = data.get('payment_title') if 'payment_title' in data.keys() else None
                order_id = data.get('order_id') if 'order_id' in data.keys() else None

                Account.objects.create(
                    telegram_id=telegram_id,
                    sb_id=sb_id,
                    account=account,
                    sum=sum,
                    name=name,
                    payment_title=payment_title,
                    kaspi_order_id=order_id
                )
                return JsonResponse({'status': True, 'message': 'Аккаунт успешно создан!',
                                     'data': [
                                         {'telegram_id': telegram_id, 'sb_id': sb_id, 'account': account,
                                          'sum': sum, "payment_title": payment_title, 'name': name}]})
    except Exception as e:
        return HttpResponse(status=200)




@csrf_exempt
def payment_handler(request):
    command = request.GET.get('command')
    txn_id = request.GET.get('txn_id')
    account = request.GET.get('account')
    sum = request.GET.get('sum', 0)
    txn_date = request.GET.get('txn_date')

    if command == 'check':
        # Логика проверки
        response = check_account(account, txn_id, sum)
    elif command == 'pay':
        # Логика оплаты
        response = process_payment(txn_id, account, sum, txn_date)
    else:
        response = {'result': 5, 'comment': 'Invalid command'}

    return JsonResponse(response)


def check_account(account, txn_id, sum):
    """
    Проверка состояния аккаунта в базе данных.

    :param account: Номер телефона или идентификатор аккаунта.
    :param txn_id: Уникальный идентификатор транзакции.
    :return: Словарь с результатом проверки.
    """
    try:
        # Ищем аккаунт в базе данных
        account_obj = Account.objects.filter(account=account).first()

        if not account_obj:
            account_obj = Account.objects.filter(phone=account).first()
            if not account_obj:
                # Если аккаунт не найден, возвращаем ошибку
                return {
                    "txn_id": txn_id,
                    "result": 1,  # Код ошибки: "аккаунт не найден"
                    "comment": "Account not found"
                }

        # Если аккаунт найден, возвращаем успешный результат

        trans: Transaction = Transaction.objects.filter(account=account).first()
        if trans:
            result = trans.result
            if result == 0:
                order_id = trans.account
                user = Account.objects.filter(account=order_id).first()
                if user is None:
                    user = Account.objects.filter(phone=account).first()

                    json_data = {
                        'name': user.name,
                        'phone': user.phone,
                        'email': user.email,
                        'sum': sum,
                        'title': user.payment_title,
                    }

                    r = requests.post(
                        url='https://vakas-tools.ru/base/regjson/af43b99/75968/',
                        json=json_data
                    )
                    logging.warning(f'STATUS ORDER -1: {r.status_code}')
                    logging.warning(f'RESULT: {r.text}')
                else:
                    client_id = user.sb_id
                    logging.warning(client_id)
                    r = requests.get(
                        f'https://chatter.salebot.pro/api/d19eb6952c1dbb66da18dcaeb374c46a/callback?client_id={client_id}&message=kaspi_success')
                    logging.warning(f'STATUS ORDER NULL: {r.status_code}')
                    logging.warning(f'RESULT: {r.text}')
                trans.delete()
                return {
                    "txn_id": txn_id,
                    "result": 0,  # Код успешной проверки,
                    "sum": Decimal(account_obj.sum),
                    "comment": "Account valid",
                    "fields": {
                        "field1": {
                            "@name": 'name',
                            "#text": user.name
                        },
                        "field2": {
                            "@name": 'name',
                            '#text': user.payment_title
                        }
                    }
                }
        else:
            return {
                    "txn_id": txn_id,
                    "result": 0,  # Код успешной проверки,
                    "sum": Decimal(account_obj.sum),
                    "comment": "Account valid",
                    "fields": {
                        "field1": {
                            "@name": 'name',
                            "#text": account_obj.name
                        },
                        "field2": {
                            "@name": 'name',
                            '#text': account_obj.payment_title
                        }
                    }
                }

    except Exception as e:
        # Обработка неожиданных ошибок
        return {
            "txn_id": txn_id,
            "result": 5,  # Код ошибки: "другая ошибка провайдера"
            "comment": f"Error occurred: {str(e)}"
        }


def process_payment(txn_id, account, sum, txn_date):
    """
    Обработка запроса на проведение платежа.

    :param txn_id: Уникальный идентификатор транзакции.
    :param account: Идентификатор абонента.
    :param sum: Сумма платежа.
    :param txn_date: Дата и время транзакции в формате YYYYMMDDHHMMSS.
    :return: Словарь с результатом обработки.
    """
    try:
        # Проверка уникальности транзакции
        transaction, created = Transaction.objects.get_or_create(txn_id=txn_id)
        if not created:
            return {
                "txn_id": txn_id,
                "result": 3,  # Код ошибки: "транзакция уже обработана"
                "comment": "Transaction already exists"
            }

        # Проверка существования аккаунта
        account_obj = Account.objects.filter(account=account).first()
        if account_obj is not None:
            if not account_obj:
                transaction.result = 1  # Код ошибки: "аккаунт не найден"
                transaction.save()
                return {
                    "txn_id": txn_id,
                    "result": 1,
                    "comment": "Account not found"
                }

            # Проверка корректности суммы
            if float(sum) <= 0:
                transaction.result = 5  # Код ошибки: "некорректная сумма"
                transaction.save()
                return {
                    "txn_id": txn_id,
                    "result": 5,
                    "comment": "Invalid payment amount"
                }

            # Преобразование даты в формат datetime
            txn_date_final = datetime.strptime(txn_date, '%Y%m%d%H%M%S') if txn_date else None

            # Запись транзакции
            transaction.account = account
            transaction.sum = float(sum)
            transaction.txn_date = txn_date_final
            transaction.result = 0  # Успешное завершение
            transaction.save()

            order_id = account_obj.account
            user = Account.objects.filter(account=order_id).first()
            client_id = user.sb_id
            logging.warning(client_id)

            r = requests.get(
                f'https://chatter.salebot.pro/api/d19eb6952c1dbb66da18dcaeb374c46a/callback?client_id={client_id}&message=kaspi_success')
            logging.warning(f'STATUS ORDER FIRST: {r.status_code}')
            logging.warning(f'RESULT: {r.text}')

            # Возврат успешного результата
            return {
                "txn_id": txn_id,
                "prv_txn": transaction.id,
                "result": 0,
                "sum": sum,
                "comment": "OK"
            }
        else:
            account_obj = Account.objects.filter(phone=account).first()
            if not account_obj:
                transaction.result = 1  # Код ошибки: "аккаунт не найден"
                transaction.save()
                return {
                    "txn_id": txn_id,
                    "result": 1,
                    "comment": "Account not found"
                }

            # Проверка корректности суммы
            if float(sum) <= 0:
                transaction.result = 5  # Код ошибки: "некорректная сумма"
                transaction.save()
                return {
                    "txn_id": txn_id,
                    "result": 5,
                    "comment": "Invalid payment amount"
                }

            # Преобразование даты в формат datetime
            txn_date_final = datetime.strptime(txn_date, '%Y%m%d%H%M%S') if txn_date else None

            # Запись транзакции
            transaction.account = account
            transaction.sum = float(sum)
            transaction.txn_date = txn_date_final
            transaction.result = 0  # Успешное завершение
            transaction.save()

            order_id = account_obj.phone
            user = Account.objects.filter(phone=order_id).first()

            json_data = {
                'name': user.name,
                'phone': user.phone,
                'email': user.email,
                'sum': user.sum,
                'title': user.payment_title,
            }

            r = requests.post(
                url='https://vakas-tools.ru/base/regjson/af43b99/75968/',
                json=json_data
            )
            logging.warning(f'STATUS ORDER SECOND: {r.status_code}')
            logging.warning(f'RESULT: {r.text}')

            # Возврат успешного результата
            return {
                "txn_id": txn_id,
                "prv_txn": transaction.id,
                "result": 0,
                "sum": sum,
                "comment": "OK"
            }
    except Exception as e:
        # Обработка ошибок
        return {
            "txn_id": txn_id,
            "result": 5,  # Код ошибки: "другая ошибка провайдера"
            "comment": f"Error occurred: {str(e)}"
        }


@csrf_exempt
def send_request_kaspi(request):
    if request.method == 'POST':
        try:
            # Парсим данные из POST-запроса
            data = json.loads(request.body)
            tran_id = data.get('tran_id')
            amount = data.get('amount')
            client_id = data.get('client_id')

            if not all([tran_id, amount, client_id]):
                logging.error("Некорректные входные данные")
                return JsonResponse({
                    'status_code': 400,
                    'error': 'Missing required parameters: tran_id, amount, or client_id'
                })

            # Логирование входных данных
            logging.info(f"Received data - TranId: {tran_id}, Amount: {amount}, ClientId: {client_id}")

            # Формируем данные для отправки
            return_url = f'https://www.aulbekova.kz/passive'
            json_data = {
                "TranId": tran_id,
                "OrderId": tran_id,
                "Amount": amount,
                "Service": "Investudy",
                "returnUrl": return_url,
                "refererHost": "api.finance-assel.kz",
                "GenerateQrCode": True
            }
            headers = {
                "Content-Type": "application/json",  # Указывает, что данные отправляются в формате JSON
                "Accept": "application/json",  # Указывает, что клиент ожидает ответ в формате JSON
                "User-Agent": "InvestudyApp/1.0",
            }

            # Отправляем POST-запрос
            response = requests.post(
                url='https://kaspi.kz/online',
                json=json_data,
                headers=headers,
                timeout=30  # Устанавливаем таймаут
            )

            # Проверяем статус ответа
            response.raise_for_status()

            # Логируем успешный результат
            logging.info(f"Request successf ul. Status code: {response.status_code}")
            logging.info(f"Response: {response.json()}")

            return JsonResponse({
                'status_code': response.status_code,
                'result': response.json()['redirectUrl']
            })

        except requests.exceptions.Timeout:
            logging.error("Превышено время ожидания ответа от сервера")
            return JsonResponse({
                'status_code': 504,
                'error': 'Request timed out. Server did not respond in time.'
            })

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP ошибка: {http_err}")
            return JsonResponse({
                'status_code': response.status_code if 'response' in locals() else 500,
                'error': str(http_err)
            })

        except requests.exceptions.RequestException as req_err:
            logging.error(f"Ошибка запроса: {req_err}")
            return JsonResponse({
                'status_code': 500,
                'error': str(req_err)
            })

        except json.JSONDecodeError:
            logging.error("Неверный формат JSON в запросе")
            return JsonResponse({
                'status_code': 400,
                'error': 'Invalid JSON'
            })

        except Exception as e:
            logging.error(f"Неизвестная ошибка: {e}")
            return JsonResponse({
                'status_code': 500,
                'error': str(e)
            })


def send_request_kaspi_tilda(phone, amount, client_id):
    try:
        # Логирование входных данных
        logging.warning(f"Received data - TranId: {phone}, Amount: {amount}, ClientId: {client_id}")

        # Формируем данные для отправки
        return_url = 'https://www.aulbekova.kz/passive'
        json_data = {
            "TranId": phone,
            "OrderId": phone,
            "Amount": amount,
            "Service": "Investudy",
            "returnUrl": return_url,
            "refererHost": "api.finance-assel.kz",
            "GenerateQrCode": True
        }

        headers = {
            "Content-Type": "application/json",  # Указывает, что данные отправляются в формате JSON
            "Accept": "application/json",  # Указывает, что клиент ожидает ответ в формате JSON
            "User-Agent": "InvestudyApp/1.0",
        }

        # Отправляем POST-запрос
        response = requests.post(
            url='https://kaspi.kz/online',
            json=json_data,
            headers=headers,
            timeout=30  # Устанавливаем таймаут
        )
        logging.warning(response.json())
        # Проверяем статус ответа
        response.raise_for_status()

        # Логируем успешный результат
        logging.warning(f"Request successful. Status code: {response.status_code}")
        logging.warning(f"Response: {response.json()}")

        return JsonResponse({
            'status_code': response.status_code,
            'result': response.json()['redirectUrl']
        })

    except requests.exceptions.Timeout:
        logging.error("Превышено время ожидания ответа от сервера")
        return JsonResponse({
            'status_code': 504,
            'error': 'Request timed out. Server did not respond in time.'
        })

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP ошибка: {http_err}")
        return JsonResponse({
            'status_code': response.status_code if 'response' in locals() else 500,
            'error': str(http_err)
        })

    except requests.exceptions.RequestException as req_err:
        logging.error(f"Ошибка запроса: {req_err}")
        return JsonResponse({
            'status_code': 500,
            'error': str(req_err)
        })

    except json.JSONDecodeError:
        logging.error("Неверный формат JSON в запросе")
        return JsonResponse({
            'status_code': 400,
            'error': 'Invalid JSON'
        })

    except Exception as e:
        logging.error(f"Неизвестная ошибка: {e}")
        return JsonResponse({
            'status_code': 500,
            'error': str(e)
        })
