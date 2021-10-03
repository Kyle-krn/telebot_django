import telebot
from main_app.models import *
from main_app.management.commands.keyboards.keyboard import *
from main_app.management.commands.keyboards.inline_keyboard import *
from django.db.models import Q

TELEGRAM_TOKEN = '2049844837:AAH-f33he41frWIkFqfV78t5f445DhtUHNk'

test_photo = 'https://inlnk.ru/mexGV'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

category_list = [x.slug for x in Category.objects.all()]
subcategory_list = [x.slug for x in SubCategory.objects.all()]
product_list = [x.slug for x in Product.objects.all()]

def update_lists():
    '''Каждый раз обновляет список для отлова хендлреов'''
    global category_list, subcategory_list, product_list
    category_list = [x.slug for x in Category.objects.all()]
    subcategory_list = [x.slug for x in SubCategory.objects.all()]
    product_list = [x.slug for x in Product.objects.all()]

@bot.message_handler(regexp='^(💰 Каталог)$')
@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'back_cat')
def catalog(message):
    '''Каталог'''
    try:
        user_id = message.chat.id
    except AttributeError:
        user_id = message.message.chat.id
        bot.delete_message(user_id, message.message.message_id)
    
    TelegramProductCartCounter.objects.filter(Q(user__chat_id=user_id) & Q(counter=True)).delete()
    update_lists()
    # Только категории в которых есть товар
    categories = Category.objects.filter(
        subcategory__product__count__gte=1).distinct()
    bot.send_message(user_id, f'Выберите категорию',
                     reply_markup=category_keyboard(categories))


@bot.callback_query_handler(func=lambda call: call.data in category_list)
@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'back_sub')
def category(call):
    '''Вывод подкатегорий'''
    if call.data.split('~')[0] == 'back_sub':
        slug = call.data.split('~')[1]
    else:
        slug = call.data
    update_lists()
    bot.delete_message(call.message.chat.id, call.message.message_id)
    try:
        category = Category.objects.get(slug=slug)
    except:
        bot.send_message(call.message.chat.id, 'Упс! Что то пошло не так')
        return
    subcategory = category.subcategory_set.filter(
        product__count__gte=1).distinct()
    bot.send_photo(chat_id=call.message.chat.id, photo=test_photo,
                   caption=f'{category.name}\n\nВыберите подкатегорию:', reply_markup=category_keyboard(subcategory, back=True))


@bot.callback_query_handler(func=lambda call: call.data in subcategory_list)
@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'back_prod')
def subcategory(call):
    '''Вывод товаров'''
    update_lists()

    if call.data.split('~')[0] == 'back_prod':
        slug = call.data.split('~')[1]
    else:
        slug = call.data
    
    TelegramProductCartCounter.objects.filter(Q(user__chat_id=call.message.chat.id) & Q(counter=True)).delete()
    bot.delete_message(call.message.chat.id, call.message.message_id)
    try:
        subcategory = SubCategory.objects.get(slug=slug)
    except:
        bot.send_message(call.message.chat.id, 'Упс, что то пошло не так')
        return
    products = subcategory.product_set.filter(count__gte=1).distinct()
    category_slug = subcategory.category.slug
    
    bot.send_photo(chat_id=call.message.chat.id, photo=test_photo,
                   caption=f'{subcategory.category.name}\n{subcategory.name}\n\nВыберите товар:', reply_markup=product_keyboard(category_slug, products))
    


@bot.callback_query_handler(func=lambda call: call.data in product_list)
@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'buy')
def product(call):
    '''Вывод продукта'''
    update_lists()
    if call.data.split('~')[0] == 'buy':
        slug = call.data.split('~')[1]
    else:
        slug = call.data
    try:
        product = Product.objects.get(slug=slug)
    except:
        bot.send_message(call.message.chat.id, 'Упс, что то пошло не так')
        return
    user = TelegramUser.objects.get(chat_id=call.message.chat.id)
    counter = TelegramProductCartCounter.objects.get_or_create(user=user, counter=True, defaults={
        'product': product,
    })

    if counter[1]:
        pass
    else:
        count = call.data.split('~')[2]            
        counter[0].count += int(count)
        if counter[0].count <= 0:   # Если юзер хочет установить кол-во 0 или меньше
            bot.answer_callback_query(callback_query_id = call.id, text='Минимум 1 штука для покупки!', show_alert = False)  # Не работает, хз почему
            counter[0].count = 1
        elif counter[0].count >= product.subcategory.category.max_count_product: # Если юзер хочет установить кол-во больше чем есть на складе
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=f'Максимальное количество товара: {product.subcategory.category.max_count_product} шт')  # Не работает, хз почему
            counter[0].count = product.subcategory.category.max_count_product
        counter[0].save()
    bot.delete_message(call.message.chat.id, call.message.message_id)
    keyboard = buy_keyboard(subcat_slug=product.subcategory.slug,
                            slug = slug, 
                            count = counter[0].count)
    bot.send_photo(chat_id=call.message.chat.id, photo=test_photo,
                   caption=f'Название - {product.title}\nЦена - {product.price}\nОписание - {product.description}\nОстаток - {product.count}', reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data == 'add_to_cart')
def add_product_in_cart(call):
    '''Добавление товара в корзину'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    cart_product = TelegramProductCartCounter.objects.get(Q(user__chat_id=call.message.chat.id) & Q(counter=True))  # Ищем каунтер клавиатуры
    product_in_cart = TelegramProductCartCounter.objects.filter(Q(user__chat_id=call.message.chat.id) & Q(counter=False) & Q(product=cart_product.product)) 
    if product_in_cart:     # Ищем такой же товар в корзине что бы пополнить его count, а не создавать новую запись, если юзер добавляет такой же товар
        if (product_in_cart[0].count + cart_product.count) > cart_product.product.subcategory.category.max_count_product:   # Если превышает максимальное кол-во  для катеогрии
            product_in_cart[0].count = cart_product.product.subcategory.category.max_count_product
        else:
            product_in_cart[0].count += cart_product.count
        
        if product_in_cart[0].count > product_in_cart[0].product.count:
            product_in_cart[0].count = product_in_cart[0].product.count
            
        product_in_cart[0].save()
        cart_product.delete()
    else:
        cart_product.counter = False
        cart_product.save()
    bot.send_message(call.message.chat.id, f'{cart_product.product.title} {cart_product.count} добавлено в корзину', reply_markup=main_keyboard())




@bot.message_handler(commands=['start', 'help'])
def command_start(message):
    data = message.chat
    update_lists()
    TelegramUser.objects.get_or_create(chat_id=data.id,
                                       defaults={
                                           'first_name': data.first_name,
                                           'last_name': data.last_name,
                                           'username': data.username
                                       })
    bot.send_message(chat_id = data.id, text='Категорически приветсвтую', reply_markup=main_keyboard())

# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def get_answer(message):
#     category = Category.objects.all()
#     update_lists()
#     bot.send_message(message.chat.id, f'ddd', reply_markup=main_keyboard())
