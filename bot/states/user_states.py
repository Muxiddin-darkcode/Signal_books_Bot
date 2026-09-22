from aiogram.fsm.state import State, StatesGroup

class BookSuggestionStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_author = State()
    waiting_for_note = State()
