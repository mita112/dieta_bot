from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
import aiomysql
from logger import logger

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