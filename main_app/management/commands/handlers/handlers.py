import telebot
from django.db.models import Q
from main_app.models import *
from main_app.management.commands.keyboards import *
from vape_shop.settings import TELEGRAM_TOKEN

test_photo = 'https://inlnk.ru/mexGV'
cat_photo = 'https://i.ytimg.com/vi/2QvOxa_7wEw/maxresdefault.jpg'
subcat_photo = 'https://i.ytimg.com/vi/jaRANdL5qrE/maxresdefault.jpg'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

category_list = [x.pk_for_telegram for x in Category.objects.all()]
subcategory_list = [x.pk_for_telegram for x in SubCategory.objects.all()]
product_list = [x.pk_for_telegram for x in Product.objects.all()]



def update_lists():
    '''Каждый раз обновляет список для отлова хендлреов'''
    global category_list, subcategory_list, product_list
    category_list = [x.pk_for_telegram for x in Category.objects.all()]
    subcategory_list = [x.pk_for_telegram for x in SubCategory.objects.all()]
    product_list = [x.pk_for_telegram for x in Product.objects.all()]



@bot.message_handler(regexp='^(💰 Каталог)$')
@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'back_cat')
def catalog(message):
    '''Вывод категорий'''
    update_lists()  
    try:
        user_id = message.chat.id
        data = message.chat
    except AttributeError:  # Если юзер попадает на данный хендлер через кнопку назад
        user_id = message.message.chat.id
        bot.delete_message(user_id, message.message.message_id)
        data = message.message.chat

    TelegramUser.objects.get_or_create(chat_id=data.id,
                                       defaults={
                                           'first_name': data.first_name,
                                           'last_name': data.last_name,
                                           'username': data.username
                                       })

    cart = TelegramProductCartCounter.objects.filter(Q(user__chat_id=user_id) & Q(counter=False))
    if PayProduct.objects.filter(user__chat_id=user_id).delete()[0]:    # Добавляем забронированные товары обратно
        for item in cart:
            item.product.count += item.count
            item.product.save()
    TelegramProductCartCounter.objects.filter(Q(user__chat_id=user_id) & Q(counter=True)).delete()  # Удаляем каунтер продукта
    categories = Category.objects.filter(subcategory__product__count__gte=1).distinct() # Только категории в которых есть товар
    bot.send_photo(chat_id=user_id, photo=cat_photo, caption=f'Выберите категорию:', reply_markup=category_keyboard(categories), parse_mode='markdown')


@bot.callback_query_handler(func=lambda call: call.data in category_list)
def category(call):
    '''Вывод подкатегорий'''
    update_lists()
    try:
        category_pk = call.data.split('||')[1]
        category = Category.objects.get(pk=category_pk)
    except:
        return bot.send_message(call.message.chat.id, 'Упс! Что то пошло не так')
    subcategory = category.subcategory_set.filter(product__count__gte=1).distinct() # Только подкатегории где есть товар
    photo = open(category.photo.path, 'rb')
    bot.edit_message_media(chat_id=call.message.chat.id, media=types.InputMediaPhoto(
        media=photo, caption=f'***Категория - {category.name}***\n\nВыберите подкатегорию:', parse_mode='markdown'), message_id=call.message.message_id, reply_markup=category_keyboard(subcategory, back=True))


@bot.callback_query_handler(func=lambda call: call.data in subcategory_list)
def subcategory(call):
    '''Вывод товаров'''
    update_lists()
    TelegramProductCartCounter.objects.filter(Q(user__chat_id=call.message.chat.id) & Q(counter=True)).delete() # Удаляем каунтер если юзер перешел по кнопке назад
    try:
        subcategory_pk = call.data.split('||')[1]
        subcategory = SubCategory.objects.get(pk=subcategory_pk)
    except:
        return bot.send_message(call.message.chat.id, 'Упс, что то пошло не так')

    products = subcategory.product_set.filter(count__gte=1).distinct()  # Товар у которого 1 или больше остатка
    category_slug = subcategory.category.pk_for_telegram
    photo = open(subcategory.photo.path, 'rb')
    bot.edit_message_media(chat_id=call.message.chat.id, media=types.InputMediaPhoto(media=photo, 
                                                         caption=f'***Категория - {subcategory.category.name}\nПодкатеогрия - {subcategory.name}***\n\nВыберите товар:', parse_mode='markdown'),   
                           message_id=call.message.message_id, 
                           reply_markup=product_keyboard(category_slug, products))


@ bot.callback_query_handler(func=lambda call: call.data in product_list)
@ bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'buy')
@ bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'search_p')
def product(call):
    '''Вывод продукта'''
    update_lists()
    if call.data.split('~')[0] == 'buy' or call.data.split('~')[0] == 'search_p':
        slug=call.data.split('~')[1]
    else:
        slug=call.data
    try:
        product_pk = slug.split('||')[1]
        product=Product.objects.get(pk=product_pk)
        if product.count <= 0:  # Если юзер на странице товара, но он закончился
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return bot.send_message(chat_id=call.message.chat.id, text='К сожалению данный товар только что закончился.')
    except:
        return bot.send_message(call.message.chat.id, 'Упс, что то пошло не так.')

    user=TelegramUser.objects.get(chat_id=call.message.chat.id)
    counter=TelegramProductCartCounter.objects.get_or_create(user=user, counter=True, defaults={   
        'product': product,
    })

    if counter[1]:  # Если каунтер только создан
        pass
    else:   # Если каунтер не создан, а существовал, обновляем его значения
        count=call.data.split('~')[2]
        counter[0].count += int(count)

        if counter[0].count > product.count:    # Если в каунтере больше кол-во чем в товаре
            bot.answer_callback_query(
            callback_query_id=call.id, text=f'Максимум {product.count} ед. товара', show_alert=False)
            counter[0].count = product.count
        else:
            if counter[0].count <= 0:   # Если юзер хочет установить кол-во 0 или меньше
                bot.answer_callback_query(
                    callback_query_id=call.id, text='Минимум 1 штука для покупки!', show_alert=False)
                counter[0].count=1
            elif counter[0].count >= product.subcategory.category.max_count_product:    # Если в канутере больше чем в макс. разрешенном для категории кол-ва
                bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=f'Максимальное количество товара: {product.subcategory.category.max_count_product} шт.')
                counter[0].count=product.subcategory.category.max_count_product
        counter[0].save()   # Сохраняем каунтер после всех веток 
    keyboard=buy_keyboard(subcat_slug=product.subcategory.pk_for_telegram,
                            slug=slug,
                            count=counter[0].count)
    photo = open(product.photo.path, 'rb')

    text = f'*Название -* {product.title}\n*Цена -* {product.price} руб.\n*Описание -* {product.description}\n*Остаток -* {product.count}шт.'

    if call.data.split('~')[0] == 'search_p':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_photo(chat_id=call.message.chat.id, photo=photo, caption=text, reply_markup=keyboard, parse_mode='markdown')
        
    bot.edit_message_media(chat_id=call.message.chat.id, 
                           media=types.InputMediaPhoto(media=photo, 
                                                       caption=text, parse_mode='markdown'),   
                           message_id=call.message.message_id, 
                           reply_markup=keyboard)
    

@ bot.callback_query_handler(func=lambda call: call.data == 'add_to_cart')
def add_product_in_cart(call):
    '''Добавление товара в корзину'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    cart_product=TelegramProductCartCounter.objects.get(Q(user__chat_id=call.message.chat.id) & Q(counter=True))  # Ищем каунтер клавиатуры
    product_in_cart=TelegramProductCartCounter.objects.filter(Q(user__chat_id=call.message.chat.id) & Q(counter=False) & Q(product=cart_product.product))  #Ищем анологичный товар в корзине
    if product_in_cart:     # Если товар найден
        if (product_in_cart[0].count + cart_product.count) > cart_product.product.subcategory.category.max_count_product:   # Если кол-во товара в корзине превышает макс. разрешенное кол-во для катеогрии
            product_in_cart[0].count=cart_product.product.subcategory.category.max_count_product
        else:
            product_in_cart[0].count += cart_product.count # Иначе просто добавляем

        if product_in_cart[0].count > product_in_cart[0].product.count: # Если в корзине больше чем есть товара на складе
            product_in_cart[0].count=product_in_cart[0].product.count

        product_in_cart[0].save()
        cart_product.delete()   # Удаляем каунтер
    else:   # Если товар не найден, делаем из каунтера
        cart_product.counter=False
        cart_product.save()
    bot.send_message(call.message.chat.id,
                     f'{cart_product.product.title}, в кол-ве {cart_product.count} шт. добавлен в корзину.', reply_markup=main_keyboard())



@ bot.message_handler(commands=['start', 'help'])
def command_start(message):
    data=message.chat
    update_lists()
    TelegramUser.objects.get_or_create(chat_id=data.id,
                                       defaults={
                                           'first_name': data.first_name,
                                           'last_name': data.last_name,
                                           'username': data.username
                                       })
    bot.send_message(
        chat_id=data.id, text='Категорически приветсвтую', reply_markup=main_keyboard())

