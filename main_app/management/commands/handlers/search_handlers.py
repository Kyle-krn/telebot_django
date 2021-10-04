from .handlers import bot
from main_app.models import *
from main_app.management.commands.keyboards import *
from django.db.models import Q


@bot.message_handler(regexp='^(Поиск товаров)$')
def search_cat_product_handlers(message):
    categories = Category.objects.filter(
        subcategory__product__count__gte=1).distinct()
    keyboard = search_category_keyboard(categories)
    bot.send_message(chat_id=message.chat.id, text='Выберите категорию', reply_markup=keyboard)
    # message = bot.send_message(message.chat.id, f"Введите название товара: ", reply_markup=cancel_next_step_keyboard())
    # bot.register_next_step_handler(message, input_title_product)




# def input_title_product(message):
#     try:
#         title = message.text
#     except Exception as e:
#         print(e)
#         message = bot.send_message(message.chat.id, f"Введите название товара: ", reply_markup=cancel_next_step_keyboard())
#         bot.register_next_step_handler(message, input_title_product)
#         return
#     product_list = Product.objects.filter(Q(title__icontains=title) & Q(count__gte=1))
#     bot.send_message(chat_id=message.chat.id, text='Выберите товар:', reply_markup=product_keyboard(sub_slug=None, products=product_list, back=False))

