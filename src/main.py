import html
import aiomysql
from babel.dates import format_date
from aiogram import Bot, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import date
from logger import logger
from config import BOT_TOKEN, dp
from handlers.kayboards import *
from handlers.In_prof import *
from handlers.states import *
from handlers.database import get_db_connection

#инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()

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