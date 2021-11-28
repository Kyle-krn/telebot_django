from .handlers import bot
from main_app.models import *
from main_app.management.commands.keyboards import *
from django.db.models import Q


@bot.message_handler(regexp='^(🔎 Поиск товаров)$')
def search_cat_product_handlers(message):
    TelegramProductCartCounter.objects.filter(Q(user__chat_id=message.chat.id) & Q(counter=True)).delete()
    data = message.chat
    TelegramUser.objects.get_or_create(chat_id=data.id,
                                       defaults={
                                           'first_name': data.first_name,
                                           'last_name': data.last_name,
                                           'username': data.username
                                       })

    categories = Category.objects.filter(
        subcategory__product__count__gte=1).distinct()
    keyboard = search_category_keyboard(categories)
    bot.send_message(chat_id=message.chat.id, text='Выберите категорию:', reply_markup=keyboard)
    # message = bot.send_message(message.chat.id, f"Введите название товара: ", reply_markup=cancel_next_step_keyboard())
    # bot.register_next_step_handler(message, input_title_product)



@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'search')
def seatch_product_handlers(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    category_slug = call.data.split('~')[1]
    TelegramUser.objects.filter(chat_id=call.message.chat.id).update(search_data=category_slug)
    message = bot.send_message(call.message.chat.id, f"Введите название товара:", reply_markup=cancel_next_step_keyboard())
    bot.register_next_step_handler(message, input_title_product)

def input_title_product(message):
    try:
        title = message.text
    except:
        return bot.send_message(chat_id=message.chat.id, text='Я понимаю только текст')
    user = TelegramUser.objects.get(chat_id=message.chat.id)
    # print(user.search_data)
    category_pk = user.search_data.split('||')[1]
    # category = Category.objects.get(pk_for_telegram=user.search_data)
    category = Category.objects.get(pk=category_pk)
    product_list = Product.objects.filter(Q(subcategory__category=category) & Q(count__gte=1) & Q(title__icontains=title))
    bot.send_message(chat_id=message.chat.id, text='Выберите товар:', reply_markup=product_keyboard(sub_slug=None, products=product_list, search=True, back=False))

