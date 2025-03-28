from aiogram.fsm.state import StatesGroup, State

class SurveyStates(StatesGroup):
    GET_IN_PROF = State()
    GET_DATE = State()
    GET_EDIT_PARAM = State()
    GET_EDIT_VALUE = State()
    READY_FOR_EDIT = State()