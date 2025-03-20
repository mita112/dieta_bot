import os
import html
import aiomysql
from babel.dates import format_date
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from datetime import date, datetime, timedelta
from typing import Optional, Callable
from typing import List
from logger import logger
from config import BOT_TOKEN, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

#инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher()

#конект к базе данных
async def get_db_connection():
    logger.debug('Подключение к базе данных...')
    try:
        conn = await aiomysql.connect(
            host=DB_HOST, 
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            cursorclass=aiomysql.DictCursor
        )
        logger.debug('Подключение к базе данных прошло успешно')
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return None 


        


#кнопки
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

async def handle_user_data(user_id, conn, colku=False):

    async with conn.cursor() as cursor:
        try:
            await cursor.execute(f"SELECT * FROM calendar_us WHERE user_id = %s", (user_id,))
            result = await cursor.fetchone()
            
            if not result:
                logger.debug(f'Создание новой колонки для пользователя {user_id} так как нет в calender_us')
                await cursor.execute(f"""
                    INSERT INTO calendar_us 
                    (user_id, date_t, calory_td, ugl_td, bel_td, jir_td)
                    VALUES (%s, %s, 0, 0, 0, 0)
                """, (user_id, date.today()))
                await conn.commit()
                return await handle_user_data(user_id, conn, colku)  # Повторный вызов после создания записи

            # Обработка смены даты
            if result['date_t'] != date.today():
                nutrients = {
                    'calo': result.get('calory_td', 0) or 0,
                    'belki': result.get('bel_td', 0) or 0,
                    'ugle': result.get('ugl_td', 0) or 0,
                    'jiri': result.get('jir_td', 0) or 0
                }

                if any(nutrients.values()):
                    logger.debug(f'создание новой записи в календаре так как сменился день {user_id}')
                    await cursor.execute("""
                        INSERT INTO daily_nutrition
                        (user_id, date, calories, proteins, fats, carbohydrates)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, result['date_t'], nutrients['calo'], nutrients['belki'], nutrients['jiri'], nutrients['ugle']))
                    logger.debug(f'обнуление данных в calender_us {user_id}')
                    await cursor.execute(f"""
                        UPDATE calendar_us 
                        SET date_t = %s, calory_td = 0, ugl_td = 0, bel_td = 0, jir_td = 0
                        WHERE user_id = %s
                    """, (date.today(), user_id))
                    
                    await conn.commit()

            await cursor.execute("SELECT COUNT(*) as count FROM daily_nutrition WHERE user_id = %s", (user_id,))
            count = (await cursor.fetchone())['count']
            logger.debug(f'результат проверки пользователя {user_id} на кол во записей в daily_n = {count}')
            if count > 30:
                logger.debug(f'удаление старой записи в календаре {user_id}')
                await cursor.execute("""
                    DELETE FROM daily_nutrition 
                    WHERE user_id = %s 
                    ORDER BY date LIMIT 1
                """, (user_id,))
                await conn.commit()

            # Возврат результата
            if colku:
                await cursor.execute(f"SELECT * FROM calendar_us WHERE user_id = %s", (user_id,))
                return (await cursor.fetchone()) or {}
            return True

        except Exception as e:
            logger.error(f"Ошибка обработки данных для {user_id}: {str(e)}")
            return False if colku else None

#команды
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} команда - /start")
    user = message.from_user
    conn = None

    try:
        conn = await get_db_connection()
        if not conn:
            await message.answer("❌ Ошибка подключения к базе данных ")
            return

        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE user_id = %s", (user.id,))
            result = await cursor.fetchone()
            logger.debug(f"Результат проверки пользователя: {result}")

            if not result:
                await cursor.execute("""
                    INSERT INTO users (user_id, weight, height, age, gender, activity_level, name, goal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user.id, 0.0, 0.0, 0, 'М', 1, user.first_name, 1))
                await conn.commit()
                await message.answer('👋 Привет я бот для помощи с диетой, для эффективного использования измени свои данные на корректные')
                await cmd_profile(message)

            else:
                await message.answer("👋 С возвращением!", reply_markup=back_to_menu_keyboard())

    except Exception as e:
        logger.fatal(f"Критическая ошибка: {e} после /start", exc_info=True)
        await message.answer("❌ Произошла внутренняя ошибка. Попробуйте позже.")
    finally:
        if conn:
            try:
                if not conn.closed:
                    await conn.ensure_closed()
            except Exception as close_error:
                logger.error(f"Ошибка при закрытии соединения: {close_error}")

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} команда - /menu")
    await message.answer(f'Меню:', reply_markup=menu_keyboard())
    
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} команда - /help")
    await message.answer("🆘 Это помощь по боту. Здесь в скором времени появится описание и возможные команды.", reply_markup=back_to_menu_keyboard())
    
@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} команда - /info")
    await message.answer("ℹ️ Информация: автор @hacker588", reply_markup=back_to_menu_keyboard())
    
@dp.message(Command("calender"))
async def cmd_calender(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} команда - /calendar")
    try:
        conn = await get_db_connection()
        if not conn:
            logger.error("Ошибка подключения к базе данных.")
            return False
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM daily_nutrition WHERE user_id = %s ORDER BY date DESC",
                (message.from_user.id,)
            )
            result = await cursor.fetchall()
            if not result:
                await message.answer('Записей пока нет')
            else:
                await message.answer('Выберите период или вернитесь в профиль', reply_markup=calender_keyboard())
    except Exception as e:
        logger.error(f'Ошибка команда /calendar {e}')
    finally:
        if conn:
            await conn.ensure_closed()
                       
@dp.message(Command("calculator"))
async def cmd_calculator(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} команда - /calculator")
    user = message.from_user
    conn = None
    try:
        logger.debug(f'Попытка подключение к БД и проверка пользователя...')
        conn = await get_db_connection()
        if not conn:
            await message.answer("❌ Ошибка подключения к базе данных ")
            return    
        user_data = await handle_user_data(user_id=message.from_user.id, conn=conn, colku=True)
        await message.answer(
            f'''<b>🔥 Ваш результат на сегодня:</b>

<b>🍽 Калории:</b> {int(user_data['calory_td'])} ккал
<b>🥩 Белки:</b> {user_data['bel_td']} г
<b>🥑 Жиры:</b> {user_data['jir_td']} г
<b>🍞 Углеводы:</b> {user_data['ugl_td']} г''', 
parse_mode="HTML", reply_markup=calculator_menu_keyboard()
            )
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Произошла ошибка при обработке вашего запроса.")
    finally:
        if conn:
            await conn.ensure_closed()
   
@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} команда - /profile")
    conn = await get_db_connection()
    cursor = await conn.cursor(aiomysql.DictCursor)
    try:
        await cursor.execute("SELECT * FROM users WHERE user_id = %s", (message.from_user.id,))
        user_data = await cursor.fetchone()
        activ = ['Сидячий образ жизни', 'Легкая активность', 'Умеренная активность', 'Высокая активность'][user_data['activity_level']-1]
        goal = ['Набрать вес', 'Похудеть', 'Нарастить мышечную массу', 'Повысить выносливость организма', 'Укрепить иммунитет', 'Придать телу рельефность', 'Поправить здоровье', 'Восстановиться после травмы', 'Стать сильнее'][user_data['goal']-1]
        if user_data:
            await message.answer(
                f"<b>👤 Профиль</b>\n"
                f"——————————————\n"
                f"<b>📛 Имя:</b> {html.escape(user_data['name'])}\n"
                f"<b>⚖️ Вес:</b> {html.escape(str(user_data['weight']))} кг\n"
                f"<b>📏 Рост:</b> {html.escape(str(user_data['height']))} см\n"
                f"<b>🎂 Возраст:</b> {html.escape(str(user_data['age']))}\n"
                f"<b>👫 Пол:</b> {html.escape(user_data['gender'])}\n"
                f"<b>🏋️ Уровень активности:</b> {html.escape(activ)}\n"
                f"<b>🎯 Цель:</b> {html.escape(goal)}\n"
                f"<b>📅 Дата регистрации:</b> {html.escape(user_data['registration_date'].strftime('%d.%m.%Y'))}\n"
                f"——————————————",
                reply_markup=profile_menu_keyboard(),
                parse_mode="HTML"
            )
        else:
            logger.error(f'Пользователь {message.from_user.id} не найден, команда /profile')
            await message.answer("❌ Пользователь не найден!", reply_markup=back_to_menu_keyboard())
    except Exception as e:
        logger.error(f'Ошибка {e} при команде /profile')
        await message.answer("❌ Произошла внутренняя ошибка. Попробуйте позже.", reply_markup=back_to_menu_keyboard())
    finally:
        logger.debug('Попытка закрыть БД после /profile...')
        try:
            await conn.ensure_closed()
            logger.debug('БД успешно закрыта после /profile')
        except Exception as e:
            logger.error(f'Oшибка {e} при попытке закрыть БД после /profile')

@dp.message(Command("change_in_pr"))
async def cmd_change_in_pr(message: types.Message):
    logger.info(f'Принял команду /сhange_in_pr от {message.from_user.id}')
    await message.answer('Выберите, что вы хотите изменить, или вернитесь в профиль', reply_markup=profile_menu_keyboard_change())

@dp.message(Command("change_in_cal"))
async def cmd_change_in_cal(message: types.Message, new=False):
    logger.info(f'Принял команду /change_in_cal от {message.from_user.id}')
    if new:
        await message.answer('Выберите, что вы хотите прибавить, или вернитесь в калькулятор', reply_markup=calculator_menu_keyboard_change())
    else:
        await message.answer('Выберите, что вы хотите изменить, или вернитесь в калькулятор', reply_markup=calculator_menu_keyboard_change1())


#функции и класс для опросника   
class SurveyStates(StatesGroup):
    GET_IN_PROF = State()
    GET_DATE = State()
    GET_EDIT_PARAM = State()
    GET_EDIT_VALUE = State()
    READY_FOR_EDIT = State()


async def change_some(user_id, column, value, data_table='users', action='update'):
    logger.debug(f'Попытка изменения {column} пользователем {user_id} в {data_table}')
    conn = None
    try:
        conn = await get_db_connection()
        if not conn:
            logger.error("Ошибка подключения к базе данных.")
            return False

        async with conn.cursor() as cursor:
            if data_table == 'calendar_us':
                await handle_user_data(user_id=user_id, conn=conn)
            query = (
                f'UPDATE {data_table} SET {column} = {column} + %s WHERE user_id = %s'
                if action == 'add' else
                f'UPDATE {data_table} SET {column} = %s WHERE user_id = %s'
            )
            logger.debug(f'Попытка внесения изменений в БД пользователь {user_id}, {column}, {data_table}...')
            await cursor.execute(query, (value, user_id))
            await conn.commit()
            logger.info(f"Параметр ({column}) пользователя {user_id} успешно изменен, {data_table}")
            return True

    except Exception as e:
        logger.error(f'Ошибка при внесении изменений в БД, {data_table} пользователь {user_id}, {column} ({e})')
        return False
    finally:  
        if conn:
            await conn.ensure_closed()


@dp.message(StateFilter(SurveyStates.GET_IN_PROF))
async def handle_value_input_prof(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    logger.debug(f"user_data: {user_data}")
    
    try:
        data_table=user_data['data_table']
    except:
        data_table='users'
    try:
        action=user_data['action']
    except:
        action='update'
        
    if user_data["column"] == 'gender':
        answer = '❌ Введите Мужчина или Женщина'
    else:
        answer = "❌ Введите положительное число!"

    user_id = message.from_user.id
    
    try:
        value =  user_data['сheck'](message.text)
        logger.debug(f'value: {value}')
        if not value:
            raise ValueError
            
        success = await change_some(
            user_id=user_id,
            column=user_data['column'],
            value=value,
            data_table=data_table,
            action=action
        )

        if success:
            if data_table == 'users':
                await message.answer("✅ Данные успешно обновлены!", reply_markup=profile_menu_keyboard_change())
            else:
                if action == 'update':
                    await message.answer("✅ Данные успешно обновлены!", reply_markup=calculator_menu_keyboard_change1())
                else:
                    await message.answer("✅ Данные успешно обновлены!", reply_markup=calculator_menu_keyboard_change())
        else:
            if data_table == 'users':
                await message.answer("❌ Ошибка при обновлении данных!", reply_markup=profile_menu_keyboard_change())
            else:
                if action == 'update':
                    await message.answer("❌ Ошибка при обновлении данных!", reply_markup=calculator_menu_keyboard_change1())
                else:
                    await message.answer("❌ Ошибка при обновлении данных!", reply_markup=calculator_menu_keyboard_change())

    except ValueError:
        await message.answer(answer)
        return
    
    await state.clear()  


async def cmd_update_weight(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены веса пользователь {message.from_user.id}")
    await state.update_data(
        column="weight",
        сheck=lambda x: float(x) if float(x) and 20 < float(x) < 300 else False,
    )
    await message.answer(f"📏 Введите свой вес (в кг)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF)

async def cmd_update_height(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены роста пользователь {message.from_user.id}")
    await state.update_data(
        column="height",
        сheck=lambda x: float(x) if float(x) and 20 < float(x) < 250 else False,
    )
    await message.answer(f"📏 Введите свой рост (в см)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF)
    
async def cmd_update_age(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены возроста пользователь {message.from_user.id}")
    await state.update_data(
        column="age",
        сheck=lambda x: int(x) if int(x) and 5 < int(x) < 131 else False,
    )
    await message.answer(f"⌛ Введите свой возраст (полных лет)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF)

async def cmd_update_gender(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены пола пользователь {message.from_user.id}")
    await state.update_data(
        column="gender",
        сheck=lambda x: x if x == 'Женщина' or x == 'Мужчина' else False,
    )
    await message.answer(f"🚻 Введите свой пол", reply_markup=gender_keyboard())
    await state.set_state(SurveyStates.GET_IN_PROF)

async def cmd_update_activity_level(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены активности пользователь {message.from_user.id}")
    await state.update_data(
        column="activity_level",
        сheck=lambda x: int(x) if int(x) in range(1, 5)  else False,
    )
    await message.answer(
'''<b>🔥 Введите свой уровень активности:</b>

1. <b>🧘 Сидячий образ жизни</b>  
   <i>Мало или нет физической активности</i>

2. <b>🏓 Легкая активность</b>  
   <i>1–3 тренировки в неделю</i>

3. <b>🏃 Умеренная активность</b>  
   <i>3–5 тренировок в неделю</i>

4. <b>🏋️‍♂️ Высокая активность</b>  
   <i>6–7 тренировок в неделю или тяжелая физическая работа</i>''',
    parse_mode="HTML", reply_markup=acivity_level_keyboard()
)
    await state.set_state(SurveyStates.GET_IN_PROF)

async def cmd_update_name(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены имени пользователь {message.from_user.id}")
    await state.update_data(
        column="name",
        сheck=lambda x: x,
    )
    await message.answer(f"📛 Введите свое имя", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF)

async def cmd_update_goal(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены цели пользователь {message.from_user.id}")
    await state.update_data(
        column="goal",
        сheck=lambda x: int(x) if int(x) in range(1, 10)  else False,
    )
    await message.answer(
    '''<b>🌟 Введите свою цель:</b>

1. <b>📈 Набрать вес</b>  
   <i>Увеличение массы тела</i>

2. <b>🥗 Похудеть</b>  
   <i>Плавное снижение веса и улучшение самочувствия</i>

3. <b>💪 Нарастить мышечную массу</b>  
   <i>Развитие мускулатуры</i>

4. <b>🚴‍♂️ Повысить выносливость организма</b>  
   <i>Улучшение физической выносливости</i>

5. <b>🧬 Укрепить иммунитет</b>  
   <i>Усиление защитных функций организма</i>

6. <b>🏆 Придать телу рельефность</b>  
   <i>Создание четкого мышечного рельефа</i>

7. <b>🩺 Поправить здоровье</b>  
   <i>Улучшение общего состояния здоровья</i>

8. <b>⚕️ Восстановиться после травмы</b>  
   <i>Реабилитация и восстановление</i>

9. <b>🦍 Стать сильнее</b>  
   <i>Развитие физической силы</i>''',
    parse_mode="HTML", reply_markup=goal_keyboard()
)
    await state.set_state(SurveyStates.GET_IN_PROF)

async def update_calories(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены параметра калькулятора пользователь {message.from_user.id}")
    await state.update_data(
        column="calory_td",
        сheck=lambda x: float(x) if float(x) and float(x) >= 0 else False,
        data_table='calendar_us'
    )
    await message.answer(f"Введите количество для 🛠️ Ккал", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF)

async def update_belki(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены параметра калькулятора пользователь {message.from_user.id}")
    await state.update_data(
        column="bel_td",
        сheck=lambda x: float(x) if float(x) and float(x) >= 0 else False,
        data_table='calendar_us'
    )
    await message.answer(f"Введите новое значение для 🛠️ Белков", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF)

async def update_jiri(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены параметра калькулятора пользователь {message.from_user.id}")
    await state.update_data(
        column="jir_td",
        сheck=lambda x: float(x) if float(x) and float(x) >= 0 else False,
        data_table='calendar_us'
    )
    await message.answer(f"ведите новое значение для 🛠️ Жиров", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF)
    
async def update_uglewodi(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены параметра калькулятора пользователь {message.from_user.id}")
    await state.update_data(
        column="ugl_td",
        сheck=lambda x: float(x) if float(x) and float(x) >= 0 else False,
        data_table='calendar_us'
    )
    await message.answer(f"Введите новое значение для 🛠️ Углеводов", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF)

async def add_calories(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены параметра калькулятора пользователь {message.from_user.id}")
    await state.update_data(
        action='add',
        column="calory_td",
        сheck=lambda x: float(x) if float(x) and float(x) >= 0 else False,
        data_table='calendar_us'
    )
    await message.answer(f"Введите количество для 🍽️ Ккал", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF) 
    
async def add_belki(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены параметра калькулятора пользователь {message.from_user.id}")
    await state.update_data(
        action='add',
        column="bel_td",
        сheck=lambda x: float(x) if float(x) and float(x) >= 0 else False,
        data_table='calendar_us'
    )
    await message.answer(f"Введите количество для 🥩 Белков", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF) 

async def add_jiri(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены параметра калькулятора пользователь {message.from_user.id}")
    await state.update_data(
        action='add',
        column="jir_td",
        сheck=lambda x: float(x) if float(x) and float(x) >= 0 else False,
        data_table='calendar_us'
    )
    await message.answer(f"Введите количество для 🥑 Жиров", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF) 
    
async def add_uglewodi(message: types.Message, state: FSMContext):
    logger.debug(f"Старт функции смены параметра калькулятора пользователь {message.from_user.id}")
    await state.update_data(
        action='add',
        column="ugl_td",
        сheck=lambda x: float(x) if float(x) and float(x) >= 0 else False,
        data_table='calendar_us'
    )
    await message.answer(f"Введите количество для 🍞 Углеводов", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_IN_PROF) 





async def cmd_nedela_in_calendar(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} команда - /day_in_calendar")
    try:
        conn = await get_db_connection()
        if not conn:
            logger.error("Ошибка подключения к базе данных.")
            return False

        async with conn.cursor() as cursor:
            await cursor.execute(
                """SELECT * 
                FROM daily_nutrition 
                WHERE 
                    user_id = %s 
                ORDER BY date DESC 
                LIMIT 7""",  # 
                (message.from_user.id,)
            )
            results = await cursor.fetchall()

            if not results:
                await message.answer('✨ <b>📭 Записей за последнюю неделю нет.')
            else:
                response = "✨ <b>📆 Ваши записи за последнюю неделю:</b> ✨\n\n"
                for record in results[::-1]:
                    formatted_date = format_date(record['date'], "EEE, dd.MM.yyyy", locale='ru').title()
    
                    response += (
                        f"▫️ <b>{formatted_date}</b>\n"
                        f"   🔥 <b>Калории:</b> <i>{record['calories']}</i> ккал\n"
                        f"   🥩 <b>Белки:</b>   {record['proteins']:>5} г\n"
                        f"   🥑 <b>Жиры:</b>     {record['fats']:>5} г\n"
                        f"   🍞 <b>Углеводы:</b> {record['carbohydrates']:>5} г\n"
                        f"\n🌿{'━'*15}🌿\n"
                    )

                await message.answer(response,
                    parse_mode="HTML", 
                    reply_markup=calender_keyboard())

    except Exception as e:
        logger.error(f'Ошибка команда /day_in_calendar {e}')
        await message.answer("❌ Произошла внутренняя ошибка. Попробуйте позже.", reply_markup=back_to_menu_keyboard())
    finally:
        if conn:
            await conn.ensure_closed()

async def cmd_month_in_calendar(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} команда - /day_in_calendar")
    try:
        conn = await get_db_connection()
        if not conn:
            logger.error("Ошибка подключения к базе данных.")
            return False

        async with conn.cursor() as cursor:
            await cursor.execute(
                """SELECT * 
                FROM daily_nutrition 
                WHERE 
                    user_id = %s 
                ORDER BY date DESC 
                LIMIT 30""",  # 
                (message.from_user.id,)
            )
            results = await cursor.fetchall()

            if not results:
                await message.answer('📭 Записей за последнюю неделю нет.')
            else:
                response = "✨ <b>📆 Ваши записи за последний месяц:</b> ✨\n\n"
                for record in results[::-1]:
                    formatted_date = format_date(record['date'], "EEE, dd.MM.yyyy", locale='ru')
    
                    response += (
                        f"▫️ <b>{formatted_date.title()}</b>\n"
                        f"   🔥 Калории: <i>{record['calories']}</i> ккал\n"
                        f"   🥩 Белки:   {record['proteins']:>5} г\n"
                        f"   🥑 Жиры:     {record['fats']:>5} г\n"
                        f"   🍞 Углеводы: {record['carbohydrates']:>5} г\n"
                        f"\n🌿{'━'*15}🌿\n"
                    )
            await message.answer(response,
                parse_mode="HTML", 
                reply_markup=calender_keyboard())
    except Exception as e:
        logger.error(f'Ошибка команда /day_in_calendar {e}')
        await message.answer("❌ Произошла внутренняя ошибка. Попробуйте позже.", reply_markup=back_to_menu_keyboard())
    finally:
        if conn:
            await conn.ensure_closed()

async def cmd_select_date(message: types.Message, state: FSMContext):
    await message.answer("Введите дату в формате ДД.ММ.ГГГГ", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_DATE)

@dp.message(StateFilter(SurveyStates.GET_DATE))
async def handle_date_input(message: types.Message, state: FSMContext):
    conn = None
    try:
        if len(message.text.split('.')) != 3:
            raise ValueError
            
        day, month, year = map(int, message.text.split('.'))
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
            raise ValueError
            
        selected_date = date(year, month, day)
        
        if selected_date > date.today():
            await message.answer("❌ Дата не может быть в будущем!")
            return

        conn = await get_db_connection()
        if not conn:
            await message.answer("❌ Ошибка подключения к базе данных")
            return

        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM daily_nutrition WHERE user_id = %s AND date = %s",
                (message.from_user.id, selected_date)
            )
            record = await cursor.fetchone()

            if record:
                formatted_date = format_date(selected_date, "EEE, dd.MMMM yyyy", locale='ru').title()
                response = (
                    f"📅 <b>{formatted_date}</b>\n\n"
                    f"🔥 Калории: {record['calories']} ккал\n"
                    f"🥩 Белки: {record['proteins']} г\n"
                    f"🥑 Жиры: {record['fats']} г\n"
                    f"🍞 Углеводы: {record['carbohydrates']} г\n\n"
                    "Выберите действие:"
                )
                
                keyboard = ReplyKeyboardBuilder()
                keyboard.add(types.KeyboardButton(text="✏️ Изменить день"))
                keyboard.add(types.KeyboardButton(text="📅🔍 Календарь"))
                keyboard.adjust(1)
                
                await message.answer(response, 
                    parse_mode="HTML", 
                    reply_markup=keyboard.as_markup(resize_keyboard=True))
                await state.update_data(selected_date=selected_date.isoformat())
                await state.set_state(SurveyStates.READY_FOR_EDIT)
            else:
                await message.answer("📭 Записей за эту дату не найдено", 
                    reply_markup=calender_keyboard())
                await state.clear()

    except ValueError:
        await message.answer("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ (например: 31.12.2023)")
    except Exception as e:
        logger.error(f"Ошибка при обработке даты: {e}")
        await message.answer("❌ Произошла ошибка при обработке даты")
        await state.clear()
    finally:  
        if conn:
            await conn.ensure_closed()

@dp.message(F.text == "✏️ Изменить день", StateFilter(SurveyStates.READY_FOR_EDIT))
async def start_edit_day(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if 'selected_date' not in data:
        await message.answer("❌ Ошибка сессии. Начните заново.")
        await state.clear()
        return
    
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        types.KeyboardButton(text="🔥 Калории"),
        types.KeyboardButton(text="🥩 Белки"),
        types.KeyboardButton(text="🥑 Жиры"),
        types.KeyboardButton(text="🍞 Углеводы"),
        types.KeyboardButton(text="❌ Отмена")
    )
    keyboard.adjust(2)
    await message.answer("Выберите параметр для изменения:", 
        reply_markup=keyboard.as_markup(resize_keyboard=True))
    await state.set_state(SurveyStates.GET_EDIT_PARAM)

@dp.message(StateFilter(SurveyStates.GET_EDIT_PARAM))
async def handle_edit_param(message: types.Message, state: FSMContext):
    param_map = {
        "🔥 Калории": "calories",
        "🥩 Белки": "proteins",
        "🥑 Жиры": "fats", 
        "🍞 Углеводы": "carbohydrates"
    }
    
    if message.text not in param_map:
        await message.answer("❌ Неверный параметр!")
        return
    
    await state.update_data(edit_param=param_map[message.text])
    await message.answer("Введите новое значение:", 
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(SurveyStates.GET_EDIT_VALUE)

@dp.message(StateFilter(SurveyStates.GET_EDIT_VALUE))
async def handle_edit_value(message: types.Message, state: FSMContext):
    conn = None
    try:
        user_data = await state.get_data()
        if 'selected_date' not in user_data or 'edit_param' not in user_data:
            await message.answer("❌ Ошибка сессии. Начните заново.")
            await state.clear()
            return
            
        selected_date = date.fromisoformat(user_data['selected_date'])
        param = user_data['edit_param']
        
        value = float(message.text)
        if value < 0:
            raise ValueError

        conn = await get_db_connection()
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM daily_nutrition WHERE user_id = %s AND date = %s",
                (message.from_user.id, selected_date)
            )
            if not await cursor.fetchone():
                await cursor.execute(
                    "INSERT INTO daily_nutrition (user_id, date) VALUES (%s, %s)",
                    (message.from_user.id, selected_date)
                )
            
            await cursor.execute(
                f"UPDATE daily_nutrition SET {param} = %s WHERE user_id = %s AND date = %s",
                (value, message.from_user.id, selected_date)
            )
            await conn.commit()
            
            await message.answer("✅ Значение успешно обновлено!", 
                reply_markup=calender_keyboard())
            
    except ValueError:
        await message.answer("❌ Введите положительное число!")
    except KeyError as e:
        logger.error(f"Отсутствует ключ в данных: {str(e)}")
        await message.answer("❌ Ошибка данных сессии. Начните заново.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении значения: {str(e)}")
        await message.answer("❌ Произошла ошибка при обновлении")
    finally:
        await state.clear()
        if conn:
            await conn.ensure_closed() 



BUTTON_HANDLERS = {
    "📋 Меню": cmd_menu,
    "🆘 Помощь": cmd_help,
    "🧮 Калькулятор": cmd_calculator,
    "ℹ️ Инфо" : cmd_info,
    "👤 Профиль" : cmd_profile,
    "🔧 Изменить": cmd_change_in_pr,
    "📅🔍 Календарь": cmd_calender,
    "📊 Неделя": cmd_nedela_in_calendar,
    "🗓️ Месяц": cmd_month_in_calendar
}

BUTTON_HANDLERS_WITH_STATE = {
    "⚖️ Вес": cmd_update_weight,
    "📏 Рост": cmd_update_height,
    "🎂 Возраст": cmd_update_age,
    "♂️♀️ Пол": cmd_update_gender,
    "🏃 Активность": cmd_update_activity_level,
    "✏️ Имя": cmd_update_name,
    "🎯 Цель": cmd_update_goal,
    "🛠️ Ккал": update_calories,
    "🛠️ Белки": update_belki,
    "🛠️ Жиры": update_jiri,
    "🛠️ Углеводы": update_uglewodi,
    "🍽️ Ккал": add_calories,
    "🥩 Белки": add_belki,
    "🥑 Жиры": add_jiri,
    "🍞 Углеводы": add_uglewodi,
    "📅 Выбрать день": cmd_select_date,
    "✏️ Изменить день": start_edit_day
}



@dp.message(F.text == "➕ Добавить")
async def handle_cal1(message: types.Message):
    logger.debug(f"Пользователь {message.from_user.id} обработка кнопки {message.text}")
    await cmd_change_in_cal(message, new=True)
    
@dp.message(F.text == "🛠️ Корректировать")
async def handle_cal2(message: types.Message):
    logger.debug(f"Пользователь {message.from_user.id} обработка кнопки {message.text}")
    await cmd_change_in_cal(message)

@dp.message(F.text.in_(BUTTON_HANDLERS))
async def handle_buttons(message: types.Message):
    logger.debug(f"Пользователь {message.from_user.id} обработка кнопки {message.text}")
    handler = BUTTON_HANDLERS[message.text]
    await handler(message)

@dp.message(F.text.in_(BUTTON_HANDLERS_WITH_STATE))
async def handle_buttons_with_state(message: types.Message, state: FSMContext):
    logger.debug(f"Пользователь {message.from_user.id} обработка кнопки {message.text}")
    handler = BUTTON_HANDLERS_WITH_STATE[message.text]
    await handler(message, state)

@dp.message(F.text == "❌ Отмена", StateFilter(SurveyStates.GET_EDIT_PARAM))
async def cancel_edit(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Изменение отменено", reply_markup=calender_keyboard())

@dp.message(F.text)
async def handle_unknown_message(message: types.Message):
    logger.warning(f"Нераспознанное сообщение от {message.from_user.id}: {message.text}")
    await message.answer(
        "⚠️ Команда не распознана\n"
        "Используйте кнопки меню или введите /help для списка команд",
        reply_markup=menu_keyboard()
    )  

if __name__ == "__main__":
    logger.info("Starting bot...")
    dp.run_polling(bot)
