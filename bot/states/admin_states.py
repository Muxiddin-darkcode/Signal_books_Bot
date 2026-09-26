from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_web_app_url = State()
    waiting_for_broadcast_message = State()
    confirm_broadcast = State()
    waiting_for_channel = State()
    waiting_for_about_text = State()
    waiting_for_contact_text = State()
    waiting_for_suggestion_reply = State()
    waiting_for_support_reply = State()

