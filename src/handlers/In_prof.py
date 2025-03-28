from datetime import date
from logger import logger
from aiogram.filters import StateFilter
from aiogram import types
from config import dp
from handlers.kayboards import *
from aiogram.types import ReplyKeyboardRemove
from handlers.states import SurveyStates
from handlers.database import get_db_connection
from aiogram.fsm.context import FSMContext

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
            if colku:
                await cursor.execute(f"SELECT * FROM calendar_us WHERE user_id = %s", (user_id,))
                return (await cursor.fetchone()) or {}
            return True

        except Exception as e:
            logger.error(f"Ошибка обработки данных для {user_id}: {str(e)}")
            return False if colku else None

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

