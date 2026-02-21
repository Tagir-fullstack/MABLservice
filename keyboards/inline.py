from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_keyboard_start():
    builder = InlineKeyboardBuilder()
    builder.button(text='🟢Создать заказ',   callback_data='Create')
    builder.button(text='📋Добавить старый заказ', callback_data='OldOrder')
    builder.button(text='✍️Изменить данные', callback_data='Edit')
    builder.button(text='♻ Обновить статус', callback_data='Finish')
    builder.button(text='📝️История заказов', callback_data='History')
    builder.adjust(1)

    keyboard = builder.as_markup()


    return keyboard

def inline_keyboard_edit_data():
    builder = InlineKeyboardBuilder()
    builder.button(text='Имя клиента',          callback_data='Edit_name')
    builder.button(text='Контактные данные',    callback_data='Edit_contact')
    builder.button(text='Устройство',           callback_data='Edit_device')
    builder.button(text='Проблему',             callback_data='Edit_problem')
    builder.button(text='Добавить коммент',     callback_data='Add_comments')
    builder.button(text='Назад',                callback_data='handler_to_main')
    builder.adjust(2)

    keyboard = builder.as_markup()

    return keyboard

def inline_keyboard_confirm_edit_data():
    builder = InlineKeyboardBuilder()
    builder.button(text='Изменить', callback_data='Confirm')
    builder.button(text='Назад',    callback_data='handler_to_main')
    builder.adjust(1)

    keyboard = builder.as_markup()

    return keyboard

def inline_keyboard_history():
    builder = InlineKeyboardBuilder()
    builder.button(text='По номеру заказа🆔', callback_data='find_by_id')
    builder.button(text='По имени клиента🪪', callback_data='find_by_name')
    builder.button(text='По моб.номеру🔢', callback_data='find_by_phone')
    builder.button(text='Назад', callback_data='handler_to_main')
    # Исправлено: builder.adjust(1) вызывался дважды подряд — убран дубликат
    builder.adjust(1)

    keyboard = builder.as_markup()

    return keyboard

def inline_keyboard_find_by_id():
    builder = InlineKeyboardBuilder()
    builder.button(text='Детальнее', callback_data='find_by_id')
    builder.button(text='Назад', callback_data='History')
    builder.adjust(1)

    keyboard = builder.as_markup()

    return keyboard

def inline_keyboard_verify_by():
    builder = InlineKeyboardBuilder()
    builder.button(text='По имени', callback_data='verify_by_name')
    builder.button(text='По номеру', callback_data='verify_by_phone')
    builder.adjust(1)

    keyboard = builder.as_markup()

    return keyboard

def inline_keyboard_find_by_back():
    builder = InlineKeyboardBuilder()
    builder.button(text='Назад', callback_data='History')
    builder.adjust(1)

    keyboard = builder.as_markup()

    return keyboard
