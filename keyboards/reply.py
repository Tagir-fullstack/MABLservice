# Удалено: from Cython.Compiler.Errors import message — неиспользуемый импорт, к проекту не относится
# Удалено: from aiogram.types.web_app_info import WebAppInfo — нигде не используется
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def reply_keyboard_end_order():
    builder = ReplyKeyboardBuilder()
    builder.button(text='В работе', callback_data='In_process')
    builder.button(text='В ожидании деталей', callback_data='Waiting_for_detail')
    builder.button(text='Успешно завершён', callback_data='Success')
    builder.button(text='Не подлежит ремонту', callback_data='Not_repairable')
    builder.button(text='Отказ клиентом', callback_data='Refused')
    builder.adjust(1)

    # Исправлено: было 'Выберите дейтсвие' (опечатка), стало 'Выберите действие'
    keyboard = builder.as_markup(resize_keyboard=True,
                                 one_time_keyboard=True,
                                 input_field_placeholder='Выберите действие')

    return keyboard


def reply_keyboard_history():
    builder = ReplyKeyboardBuilder()
    builder.button(text='Найти по номеру заказа', callback_data='find_by_id')
    builder.button(text='Найти по имени клиента', callback_data='find_by_name')
    builder.button(text='Найти по названию устройства', callback_data='find_by_device')
    builder.adjust(1)

    keyboard = builder.as_markup()

    return keyboard


def reply_keyboard_status():
    builder = ReplyKeyboardBuilder()
    builder.button(text='В работе', callback_data='In_process')
    builder.button(text='В ожидании деталей', callback_data='Waiting_for_detail')
    builder.button(text='Выполнен на месте', callback_data='Done')
    builder.adjust(1)

    # Исправлено: было 'Выберите дейтсвие' (опечатка), стало 'Выберите действие'
    keyboard = builder.as_markup(resize_keyboard=True,
                                 one_time_keyboard=True,
                                 input_field_placeholder='Выберите действие')

    return keyboard
