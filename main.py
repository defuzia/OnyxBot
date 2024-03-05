from datetime import datetime, timedelta

from telebot import TeleBot

from middlewares import *

bot = TeleBot("6885824087:AAGGtcnNjV8AqOwOXJaed_dxiW0zqY2JgNA")


@bot.message_handler(commands=["start"])
def start(message):
    start_message = f"Вітаємо {message.from_user.first_name}"
    bot.send_message(message.chat.id, start_message, reply_markup=make_main_markup())
    create_user(message.from_user.id)


@bot.message_handler(func=lambda message: message.text == "🛒Загальний каталог")
def main_catalogue(message):
    display_item(message, 0, len(get_all_items()) - 1)


def display_item(message, start_index, end_index):
    item = get_all_items()[start_index]
    item_id, name, photo, status, arrival_date, price = item

    markup = make_item_markup(start_index, end_index, status, item_id)

    text = f"{name} - {status}\nЦіна: {price}$"
    if status == "Out of stock":
        text += f"\nОрієнтовна дата доставки: {arrival_date}"

    bot.send_photo(message.chat.id, get_ready_image(photo), text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("order_item:"))
def order_item(call):
    item_id = int(call.data.split(":")[1])

    bot.send_message(call.message.chat.id, "Виберіть поштову систему якою ми відправимо вам товар: ",
                     reply_markup=make_delivery_system_markup(item_id))


@bot.callback_query_handler(func=lambda call: call.data.startswith("nowa_poshta:"))
def nowa_poshta(call):
    item_id, name, photo, _, _, price = get_item(call.data.split(":")[1])[0]
    order_info = item_id, name, get_ready_image(photo), price + 120, "Нова Пошта"
    future_date = datetime.now().date() + timedelta(days=7)
    text = f"""
Ви обрати доставку Новою Поштою 🔴\n
Орієнтовний термін прибуття ~ {future_date}, ціна доставки 120$\n

Будь ластка введіть ваші данні для відправки\n
⚠️Формат введення(з комами)⚠️: \n\nІм'я Прізвище, +380********, Місто, Номер_відділення\n
    """
    bot.send_message(call.message.chat.id, text)

    bot.register_next_step_handler(call.message, check_recipient_info, order_info)


@bot.callback_query_handler(func=lambda call: call.data.startswith("ukr_poshta:"))
def ukr_poshta(call):
    item_id, name, photo, _, _, price = get_item(call.data.split(":")[1])[0]
    order_info = item_id, name, get_ready_image(photo), price + 70, "Укр Пошта"
    future_date = datetime.now().date() + timedelta(days=12)
    text = f"""
Ви обрати доставку Укр Поштою 🟡\n
Орієнтовний термін прибуття ~ {future_date}, ціна доставки 70$\n
    
Будь ластка введіть ваші данні для відправки\n
⚠️Формат введення(з комами)⚠️: \n\nІм'я Прізвище, +380********, Місто, Номер_відділення\n
    """
    bot.send_message(call.message.chat.id, text)

    bot.register_next_step_handler(call.message, check_recipient_info, order_info)


def check_recipient_info(message, order_info):
    recipient_info_list = message.text.split(",")
    item_id, name, photo, price, selected_delivery_system = order_info
    if (len(recipient_info_list) != 4
            or len(recipient_info_list[0].split(" ")) != 2
            or not recipient_info_list[1].strip(" ").startswith("+380")
            or not recipient_info_list[3].strip(" ").isdigit()):
        bot.send_message(message.chat.id, "🤨Невірно введені данні, перевірте правильність данних та замовте товар знову")
    else:
        text = f"""
        Чудово, Ваше замолення оформлене та чекає розгляду, Ви можете перевірити статус замолення нажавши відповідну кнопку ⬇️\n\n
        
{name}\n
Вибраний поштовий сервіс: {selected_delivery_system}\n\n
До сплати: {price}$\n
        """
        bot.send_photo(message.chat.id, photo, text)

        if selected_delivery_system == "Нова Пошта":
            estimated_arrival_date = datetime.now().date() + timedelta(days=7)
        else:
            estimated_arrival_date = datetime.now().date() + timedelta(days=7)

        add_order_to_user_orders(message.from_user.id, item_id, selected_delivery_system, estimated_arrival_date,
                                 "Обробка", message.text)


@bot.callback_query_handler(func=lambda call: call.data == "promo_code")
def promo_code(call):
    bot.send_message(call.message.chat.id, "In development")


@bot.callback_query_handler(func=lambda call: call.data == "get_setka")
def get_setka(call):
    bot.send_photo(call.message.chat.id, get_ready_image("setka.jpg"))
    bot.send_photo(call.message.chat.id, get_ready_image("setka1.jpg"))


@bot.callback_query_handler(func=lambda call: call.data.startswith("previous_item:"))
def previous_item(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    data = call.data.split(":")
    if int(data[1]) == 0:
        start_index = int(data[2])
        display_item(call.message, start_index, int(data[2]))
    else:
        start_index = int(data[1]) - 1
        display_item(call.message, start_index, int(data[2]))


@bot.callback_query_handler(func=lambda call: call.data.startswith("next_item:"))
def next_item(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    data = call.data.split(":")
    if int(data[1]) == int(data[2]):
        start_index = 0
        display_item(call.message, start_index, int(data[2]))
    else:
        start_index = int(data[1]) + 1
        display_item(call.message, start_index, int(data[2]))


@bot.message_handler(func=lambda message: message.text == "📍Каталог товарів в наявності")
def in_stock_catalogue(message):
    display_in_stock_item(message, 0, len(get_in_stock_items()) - 1)


def display_in_stock_item(message, start_index, end_index):
    item = get_in_stock_items()[start_index]
    item_id, name, photo, _, _, price = item

    markup = make_in_stock_item_markup(start_index, end_index, item_id)

    text = f"{name}\nЦіна: {price}$"

    bot.send_photo(message.chat.id, get_ready_image(photo), text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("previous_in_stock_item:"))
def previous_in_stock_item(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    data = call.data.split(":")
    if int(data[1]) == 0:
        start_index = int(data[2])
        display_in_stock_item(call.message, start_index, int(data[2]))
    else:
        start_index = int(data[1]) - 1
        display_in_stock_item(call.message, start_index, int(data[2]))


@bot.callback_query_handler(func=lambda call: call.data.startswith("next_in_stock_item:"))
def next_in_stock_item(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    data = call.data.split(":")
    if int(data[1]) == int(data[2]):
        start_index = 0
        display_in_stock_item(call.message, start_index, int(data[2]))
    else:
        start_index = int(data[1]) + 1
        display_in_stock_item(call.message, start_index, int(data[2]))


@bot.message_handler(func=lambda message: message.text == "🆘Звязатись з менеджером")
def contact_the_manager(message):
    text = """
Виберіть опцію за допомогою якою ми зможемо з Вами зв'язатись 📞\n\n
⚠️Зверніть увагу, при виборі опції⚠️:\n 
Зв'язатись по нікнейму Telegram формат вводу: @ваш_нікнейм\n
Зв'язатись по номеру телефону формат вводу: +380********
        """
    bot.send_message(message.chat.id, text, reply_markup=make_contact_the_manager_markup())


@bot.callback_query_handler(func=lambda call: call.data == "contact_by_the_nick_name")
def contact_by_the_nick_name(call):
    text = "⚠️Введіть свій нікнейм в Telegram, зверніть увагу, формат вводу: @ваш_нікнейм⚠️"

    bot.send_message(call.message.chat.id, text)

    bot.register_next_step_handler(call.message, check_nick_name)


def check_nick_name(message):
    if message.text.startswith("@"):
        bot.send_message(message.chat.id, "Дякуємо ❤️, ми звяжемось з Вами орієнтовно за 15 хвилин)")
    else:
        bot.send_message(message.chat.id, "🤨Неправильний формат нікнейму, попробуйте знову")


@bot.callback_query_handler(func=lambda call: call.data == "contact_by_the_phone_number")
def contact_by_the_phone_number_name(call):
    text = "⚠️Введіть свій номер телефону, зверніть увагу формат вводу: +380********⚠️"

    bot.send_message(call.message.chat.id, text)

    bot.register_next_step_handler(call.message, check_phone_number)


def check_phone_number(message):
    if message.text.startswith("+380") and len(message.text) == 13:
        bot.send_message(message.chat.id, "Дякуємо ❤️, ми звяжемось з вами орієнтовно за 15 хвилин)")
    else:
        bot.send_message(message.chat.id, "🤨Неправильний формат номеру телефону, попробуйте знову")


@bot.message_handler(func=lambda message: message.text == "📦Перевірити статус замовлення")
def check_order_status(message):
    user_orders = get_user_orders(message.from_user.id)
    for order in user_orders:
        _, _, item_id, selected_delivery_system, estimated_arrival_date, status, user_info = order
        _, name, photo, _, _, _ = get_item(item_id)[0]
        text = f"""
Замовлення: {name}\n
Вибрана поштова система: {selected_delivery_system}\n
Статус: {status}, орієнтовна дата прибуття: {estimated_arrival_date}\n
Інформація замовника: {user_info}
        """
        bot.send_photo(message.chat.id, get_ready_image(photo), text)


if __name__ == "__main__":
    bot.polling(none_stop=True)
