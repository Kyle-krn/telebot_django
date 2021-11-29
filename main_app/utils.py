from main_app.forms import OrderChangeForm


def change_item_order_utils(instance, request):
    '''Изменение кол-ва товра в неоплаченных заказах (заказы через сайт и через мендежра в боте)'''
    form = OrderChangeForm(request.POST)
    if form.is_valid():
        cf = form.cleaned_data
        instance.count = cf['count']
        instance.save()
        instance.order.set_order_price()