from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from logger import logger


def calender_keyboard() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="👤 Профиль"),
        types.KeyboardButton(text="📊 Неделя"),
        types.KeyboardButton(text="🗓️ Месяц"),
        types.KeyboardButton(text="📅 Выбрать день")
    )
    builder.adjust(2, 2, 2)
    return builder.as_markup(resize_keyboard=True)

def acivity_level_keyboard() -> types.ReplyKeyboardMarkup:
    logger.debug('Инициализация клавиатуры уровень активности')
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='1'),
        types.KeyboardButton(text='2'),
        types.KeyboardButton(text='3'),
        types.KeyboardButton(text='4')
    )
    builder.adjust(4)
    return builder.as_markup(resize_keyboard=True)

def gender_keyboard() -> types.ReplyKeyboardMarkup:
    logger.debug('Инициализация клавиатуры уровень активности')
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='Мужчина'),
        types.KeyboardButton(text='Женщина')
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def goal_keyboard() -> types.ReplyKeyboardMarkup:
    logger.debug('Инициализация клавиатуры цель')
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text='1'),
        types.KeyboardButton(text='2'),
        types.KeyboardButton(text='3'),
        types.KeyboardButton(text='4'),
        types.KeyboardButton(text='5'),
        types.KeyboardButton(text='6'),
        types.KeyboardButton(text='7'),
        types.KeyboardButton(text='8'),
        types.KeyboardButton(text='9')
    )
    builder.adjust(3, 3, 3)
    return builder.as_markup(resize_keyboard=True)

def back_to_menu_keyboard() -> types.ReplyKeyboardMarkup:
    logger.debug('Инициализация клавиатуры вернутся в меню')
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="📋 Меню"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def profile_menu_keyboard() -> types.ReplyKeyboardMarkup:
    logger.debug('Инициализация клавиатуры меню профиля')
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="📋 Меню"),
        types.KeyboardButton(text="🔧 Изменить"),
        types.KeyboardButton(text="📅🔍 Календарь")
    )
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def profile_menu_keyboard_change() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="👤 Профиль"),
        types.KeyboardButton(text="⚖️ Вес"),
        types.KeyboardButton(text="📏 Рост"),
        types.KeyboardButton(text="🎂 Возраст"),
        types.KeyboardButton(text="♂️♀️ Пол"),
        types.KeyboardButton(text="🏃 Активность"),
        types.KeyboardButton(text="✏️ Имя"),
        types.KeyboardButton(text="🎯 Цель")
    )
    builder.adjust(3, 3, 2)  # 4 ряда по 2 кнопки
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите команду..."
    )

def menu_keyboard() -> types.ReplyKeyboardMarkup:
    logger.debug('Инициализация клавиатуры меню')
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="ℹ️ Инфо"),
        types.KeyboardButton(text="🆘 Помощь"),
        types.KeyboardButton(text="🧮 Калькулятор"),
        types.KeyboardButton(text="👤 Профиль")
    )
    builder.adjust(2, 2) 
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите команду..."
    )

def calculator_menu_keyboard() -> types.ReplyKeyboardMarkup:
    logger.debug('Инициализация клавиатуры меню калькулятора')
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="➕ Добавить"),
        types.KeyboardButton(text="📋 Меню"),
        types.KeyboardButton(text="🛠️ Корректировать")
    )
    builder.adjust(1, 2)
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите команду..."
    )

def calculator_menu_keyboard_change() -> types.ReplyKeyboardMarkup:
    logger.debug('Инициализация клавиатуры меню калькулятора изменения')
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="🍽️ Ккал"),
        types.KeyboardButton(text="🥩 Белки"),
        types.KeyboardButton(text="🥑 Жиры"),
        types.KeyboardButton(text="🍞 Углеводы"),
        types.KeyboardButton(text="🧮 Калькулятор")
    )
    builder.adjust(2, 2, 1)
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите команду..."
    )
    
def calculator_menu_keyboard_change1() -> types.ReplyKeyboardMarkup:
    logger.debug('Инициализация клавиатуры меню калькулятора изменения')
    builder = ReplyKeyboardBuilder()
    builder.add(
        types.KeyboardButton(text="🛠️ Ккал"),
        types.KeyboardButton(text="🛠️ Белки"),
        types.KeyboardButton(text="🛠️ Жиры"),
        types.KeyboardButton(text="🛠️ Углеводы"),
        types.KeyboardButton(text="🧮 Калькулятор")
    )
    builder.adjust(2, 2, 1)
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите команду..."
    )