import telebot
from main_app.models import *
from main_app.management.commands.keyboards.keyboard import *
from main_app.management.commands.keyboards.inline_keyboard import *


TELEGRAM_TOKEN = '2049844837:AAH-f33he41frWIkFqfV78t5f445DhtUHNk'
bot = telebot.TeleBot(TELEGRAM_TOKEN)
category_list = [x.slug for x in Category.objects.all()] 
subcategory_list = [x.slug for x in SubCategory.objects.all()] 
product_list = [x.slug for x in Product.objects.all()] 


@bot.message_handler(regexp='^(💰 Каталог)$')
def catalog(message):
    '''Каталог'''
    # global category_list
    # category_list = [x.slug for x in Category.objects.all()]

    categories = Category.objects.filter(subcategory__product__isnull=False).distinct()  # Только категории в которых есть товар
    categories = Category.objects.all()
    print(categories)
    bot.send_message(message.chat.id, f'Выбирай', reply_markup=category_keyboard(categories))


@bot.callback_query_handler(func=lambda call: call.data in category_list)
def category(call):
    '''Вывод категорий'''
    # global subcategory_list
    # subcategory_list = [x.slug for x in SubCategory.objects.all()] 

    bot.delete_message(call.message.chat.id, call.message.message_id)
    try:
        category = Category.objects.get(slug=call.data)
    except:
        bot.send_message(call.message.chat.id, 'Упс! Что то пошло не так')
        return
    
    # Здесь должно быть фото
    bot.send_message(call.message.chat.id, f'{category.name}\n\nВыберите подкатегорию:', reply_markup=category_keyboard(category.subcategory_set.all()))


@bot.callback_query_handler(func=lambda call: call.data in subcategory_list)
def subcategory(call):
    '''Вывод подкатегорий'''
    bot.delete_message(call.message.chat.id, call.message.message_id)
    try:
        subcategory = SubCategory.objects.get(slug=call.data)
    except:
        bot.send_message(call.message.chat.id, 'Упс, что то пошло не так')
        return
    products = subcategory.product_set.filter(count__gte=1)
    print(products)
    bot.send_message(call.message.chat.id, f'{subcategory.category.name}\n{subcategory.name}\n\nВыберите товар:', reply_markup=product_keyboard(products))


@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_answer(message):
    category = Category.objects.all()
    bot.send_message(message.chat.id, f'ddd', reply_markup=main_keyboard())


