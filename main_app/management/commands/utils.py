import requests
import random
import string
from vape_shop.settings import QIWI_TOKEN

def check_price_delivery(post_index, weight):
    '''Расчет стоймости доставки'''
    url = 'https://postprice.ru/engine/russia/api.php'
    data = {
        'from': 610002,
        'to': post_index,
        'mass': weight,
    }
    req = requests.get(url, data).json()
    return sorted([req['pkg'], req['pkg_1class']])[0]


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


def get_pay_in(api_access_token):
    '''Берет последние 25 входящих платежей на киви'''
    s7 = requests.Session()
    s7.headers['Accept']= 'application/json'
    s7.headers['authorization'] = 'Bearer ' + api_access_token
    parameters = {'rows': 25, 'operation': "IN"}
    p = s7.get('https://edge.qiwi.com/payment-history/v2/persons/79006292609/payments', params = parameters)
    return p.json()

def check_qiwi(comment, price):
    list_pay = get_pay_in(QIWI_TOKEN)
    for payment in list_pay['data']:
        comment_pay = payment['comment']
        price_pay = payment['sum']['amount']
        if comment_pay == comment and price_pay == price:
            return True
    return False


def generate_alphanum_random_string(length):
    """Генератор рандомных строк типа - s4Knf3Lf35"""
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string