import requests
import random
import string
from main_app.models import QiwiToken
from vape_shop.settings import QIWI_TOKEN
import smtplib                                      # Импортируем библиотеку по работе с SMTP

from email.mime.multipart import MIMEMultipart      # Многокомпонентный объект
from email.mime.text import MIMEText                # Текст/HTML
from email.mime.image import MIMEImage              # Изображения

def check_price_delivery(post_index, weight):
    '''Расчет стоймости доставки'''
    url = 'https://postprice.ru/engine/russia/api.php'
    data = {
        'from': 610002,
        'to': post_index,
        'mass': weight,
    }
    req = requests.get(url, data).json()
    delibery_pay = sorted([req['pkg'], req['pkg_1class']])[0]
    return int(float(delibery_pay))


def check_time_delivery(post_index, weight):
    url = 'https://tariff.pochta.ru/v1/calculate/delivery'
    data = {
        'json': '',
        'object': 47030,    # Посылка
        'pack': 99,  # Упаковка коробка M
        'from': 610002,  # От кого
        'to': post_index,   # Кому
        'weight': weight
    }
    req = requests.get(url, data).json()
    return req["delivery"]["max"]


def get_pay_qiwi_in(api_access_token, number):
    '''Берет последние 25 входящих платежей на киви'''
    s7 = requests.Session()
    s7.headers['Accept']= 'application/json'
    s7.headers['authorization'] = 'Bearer ' + api_access_token
    parameters = {'rows': 25, 'operation': "IN"}
    p = s7.get(f'https://edge.qiwi.com/payment-history/v2/persons/{number}/payments', params = parameters)
    return p.json()


def get_qiwi_balance(login, api_access_token):
    s = requests.Session()
    s.headers['Accept']= 'application/json'
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    b = s.get('https://edge.qiwi.com/funding-sources/v2/persons/' + login + '/accounts')
    data = b.json()
    rubAlias = [x for x in data['accounts'] if x['alias'] == 'qw_wallet_rub']
    rubBalance = rubAlias[0]['balance']['amount']
    return rubBalance

def check_qiwi(comment, price):
    token = QiwiToken.objects.get(active=True)
    try:
        list_pay = get_pay_qiwi_in(token.token, token.number)
        for payment in list_pay['data']:
            comment_pay = payment['comment']
            price_pay = payment['sum']['amount']
            if comment_pay == comment and price_pay == price:
                return True
        return False
    except:
        return 'error'


def generate_alphanum_random_string(length):
    """Генератор рандомных строк типа - s4Knf3Lf35"""
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string


def send_email(text):
    addr_from = r"bot3888callback@gmail.com"                 # Адресат
    addr_to = "dolinv@internet.ru"

    password  = "Bot3888callback*&!/."                                  # Пароль
    # password  = "iphone95"                                  # Пароль
    msg = MIMEMultipart()                               # Создаем сообщение
    msg['From']    = addr_from                          # Адресат
    msg['To']      = addr_to                            # Получатель
    msg['Subject'] = 'Тема сообщения'
    body = text

    msg.attach(MIMEText(body, 'plain'))                 # Добавляем в сообщение текст
    ctype = 'application/octet-stream'  # Будем использовать общий тип
    maintype, subtype = ctype.split('/', 1)  # Получаем тип и подтип

    # file.add_header('Content-Disposition', 'attachment', filename=filename) # Добавляем заголовки


    server = smtplib.SMTP(host='smtp.gmail.com: 587')         # Создаем объект SMTP
    server.set_debuglevel(True)                         # Включаем режим отладки - если отчет не нужен, строку можно закомментировать
    server.starttls()                                   # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)                 # Получаем доступ
    server.send_message(msg)                            # Отправляем сообщение
    server.quit()

