import requests
from main_app.forms import OrderChangeForm


def change_item_order_utils(instance, request):
    '''Изменение кол-ва товра в неоплаченных заказах (заказы через сайт и через мендежра в боте)'''
    form = OrderChangeForm(request.POST)
    if form.is_valid():
        cf = form.cleaned_data
        instance.count = cf['count']
        instance.save()
        instance.order.set_order_price()


def delete_order_utils(order):
    '''Полностью удаляет неоплаченный заказ '''
    for item in order.soldproduct.all():
        item.delete()
    order.delete()


def remove_item_order_utils(instance):
    '''Удалеят товар из заказа'''
    order = instance.order
    instance.delete()
    order.set_order_price()


def check_price_delivery(post_index, weight):
    '''Расчет стоймости доставки'''
    url = 'https://postprice.ru/engine/russia/api.php'
    post_index = int(post_index)
    data = {
        'from': 610002,
        'to': post_index,
        'mass': weight,
    }
    req = requests.get(url, data).json()
    if weight <= 200:
        return int(float(req['pkg_1class']))
    elif weight <= 20000:
        return int(float(req['pkg']))
    else:
        total_sum = 0
        x = weight // 20000
        for i in range(x):
            data['mass'] = 20000
            req = requests.get(url, data).json()
            total_sum += int(float(req['pkg']))
        
        if weight % 20000 != 0:
            y = weight % 20000
            data['mass'] = y
            req = requests.get(url, data).json()
            total_sum += int(float(req['pkg']))
        return total_sum


def check_time_delivery(post_index, weight):
    '''Расчет времени доставки, в приложении пока не используется'''
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