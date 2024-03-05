from telebot import types

from sql_handler import SQLFork


def create_user(user_id):
    query = f'INSERT OR IGNORE INTO users (user_id) VALUES ({user_id});'
    SQLFork('INSERT').execute_sql(query)


def get_all_items():
    query = f'SELECT * FROM goods'
    return SQLFork('SELECT').execute_sql(query)


def get_in_stock_items():
    query = f'SELECT * FROM goods WHERE status = "In stock"'
    return SQLFork('SELECT').execute_sql(query)


def get_item(item_id):
    query = f'SELECT * FROM goods WHERE id = {item_id}'
    return SQLFork('SELECT').execute_sql(query)


def get_ready_image(image):
    image_path = f'images/{image}'
    with open(image_path, 'rb') as image_file:
        image = image_file.read()

    return image


def add_order_to_user_orders(user_id, item_id, selected_delivery_system, estimated_arrival_date, status, user_info):
    query = f'INSERT INTO user_orders (related_user, related_item, selected_delivery_system, estimated_arrival_date, status, user_info) VALUES ({user_id}, {item_id}, "{selected_delivery_system}", "{str(estimated_arrival_date)}", "{status}", "{user_info}");'
    SQLFork('INSERT').execute_sql(query)


def get_user_orders(user_id):
    query = f'SELECT * FROM user_orders WHERE related_user = {user_id}'
    return SQLFork('SELECT').execute_sql(query)


def make_main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    main_catalogue_button = types.KeyboardButton("🛒Загальний каталог")
    in_stock_catalogue_button = types.KeyboardButton("📍Каталог товарів в наявності")
    contact_the_manager_button = types.KeyboardButton("🆘Звязатись з менеджером")
    check_order_status_button = types.KeyboardButton("📦Перевірити статус замовлення")

    markup.add(main_catalogue_button, in_stock_catalogue_button)
    markup.add(contact_the_manager_button, check_order_status_button)

    return markup


def make_contact_the_manager_markup():
    markup = types.InlineKeyboardMarkup()

    contact_by_the_nick_name_button = types.InlineKeyboardButton("🌀По нікнейму Telegram",
                                                                 callback_data="contact_by_the_nick_name")
    contact_by_the_phone_number_button = types.InlineKeyboardButton("📞По номеру телефону",
                                                                    callback_data="contact_by_the_phone_number")

    markup.row(contact_by_the_nick_name_button)
    markup.row(contact_by_the_phone_number_button)

    return markup


def make_item_markup(start_index, end_index, status, item_id):
    markup = types.InlineKeyboardMarkup()

    order_item_button = types.InlineKeyboardButton("🛍Замовити", callback_data=f"order_item:{item_id}")
    get_setka_button = types.InlineKeyboardButton("📐Розмірна сітка", callback_data="get_setka")
    promo_code_button = types.InlineKeyboardButton("🎁Використати промокод", callback_data="promo_code")
    previous_item_button = types.InlineKeyboardButton("⬅️",
                                                      callback_data=f"previous_item:{start_index}:{end_index}")
    index_of_item_button = types.InlineKeyboardButton(f"№{start_index + 1}/{end_index + 1}", callback_data=" ")
    next_item_button = types.InlineKeyboardButton("➡️",
                                                  callback_data=f"next_item:{start_index}:{end_index}")

    if status == "Out of stock":
        markup.row(get_setka_button)
    else:
        markup.row(order_item_button, get_setka_button)
        markup.row(promo_code_button)

    markup.row(previous_item_button, index_of_item_button, next_item_button)

    return markup


def make_in_stock_item_markup(start_index, end_index, item_id):
    markup = types.InlineKeyboardMarkup()

    order_item_button = types.InlineKeyboardButton("🛍Замовити", callback_data=f"order_item:{item_id}")
    get_setka_button = types.InlineKeyboardButton("📐Розмірна сітка", callback_data="get_setka")
    promo_code_button = types.InlineKeyboardButton("🎁Використати промокод", callback_data="promo_code")
    previous_in_stock_item_button = types.InlineKeyboardButton("⬅️",
                                                      callback_data=f"previous_in_stock_item:{start_index}:{end_index}")
    index_of_item_button = types.InlineKeyboardButton(f"№{start_index + 1}/{end_index + 1}", callback_data=" ")
    next_in_stock_item_button = types.InlineKeyboardButton("➡️",
                                                  callback_data=f"next_in_stock_item:{start_index}:{end_index}")

    markup.row(order_item_button, get_setka_button)
    markup.row(promo_code_button)
    markup.row(previous_in_stock_item_button, index_of_item_button, next_in_stock_item_button)

    return markup


def make_delivery_system_markup(item_id):
    markup = types.InlineKeyboardMarkup()

    nowa_poshta_button = types.InlineKeyboardButton("🔴Нова Пошта", callback_data=f"nowa_poshta:{item_id}")
    ukr_poshta_button = types.InlineKeyboardButton("🟡Укр Пошта", callback_data=f"ukr_poshta:{item_id}")

    markup.row(nowa_poshta_button, ukr_poshta_button)

    return markup
