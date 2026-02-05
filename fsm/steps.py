from aiogram.fsm.state import State, StatesGroup


class AddData(StatesGroup):
    GET_NAME = State()
    GET_PHONE = State()
    GET_DEVICE = State()
    GET_PROBLEM = State()
    GET_STATUS = State()
    GET_COMMENTS = State()


class EditData(StatesGroup):
    GET_ID = State()
    CONFIRM_EDIT = State()
    GIVE_DATA = State()
    EDIT_NAME = State()
    EDIT_PHONE = State()
    EDIT_DEVICE = State()
    EDIT_PROBLEM = State()
    ADD_COMMENTS = State()


class FinishOrder(StatesGroup):
    GET_ID = State()
    FINISH_ORDER = State()


class OrderHistory(StatesGroup):
    GET_ID = State()
    ORDER_ID = State()
    ORDER_NAME = State()
    ORDER_PHONE = State()


class ClientSteps(StatesGroup):
    GET_ID = State()
    GET_NAME = State()
    GET_PHONE = State()
