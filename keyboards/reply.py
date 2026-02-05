# Удалено: from Cython.Compiler.Errors import message — неиспользуемый импорт, к проекту не относится
# Удалено: from aiogram.types.web_app_info import WebAppInfo — нигде не используется
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def reply_keyboard_end_order():
    builder = ReplyKeyboardBuilder()
    builder.button(text='В работе')
    builder.button(text='В ожидании деталей')
    builder.button(text='Успешно завершён')
    builder.button(text='Не подлежит ремонту')
    builder.button(text='Отказ клиентом')
    builder.adjust(1)

    # Исправлено: было 'Выберите дейтсвие' (опечатка), стало 'Выберите действие'
    keyboard = builder.as_markup(resize_keyboard=True,
                                 one_time_keyboard=True,
                                 input_field_placeholder='Выберите действие')

    return keyboard


def reply_keyboard_history():
    builder = ReplyKeyboardBuilder()
    builder.button(text='Найти по номеру заказа')
    builder.button(text='Найти по имени клиента')
    builder.button(text='Найти по названию устройства')
    builder.adjust(1)

    keyboard = builder.as_markup()

    return keyboard


def reply_keyboard_status():
    builder = ReplyKeyboardBuilder()
    builder.button(text='В работе')
    builder.button(text='В ожидании деталей')
    builder.button(text='Выполнен на месте')
    builder.adjust(1)

    # Исправлено: было 'Выберите дейтсвие' (опечатка), стало 'Выберите действие'
    keyboard = builder.as_markup(resize_keyboard=True,
                                 one_time_keyboard=True,
                                 input_field_placeholder='Выберите действие')

    return keyboard
