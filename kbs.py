from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder



# def get_keyboard():
#     return ReplyKeyboardMarkup(
#         keyboard=[s
#             [KeyboardButton(text="Upload a story")],
#             [KeyboardButton(text="Read a story")],
#         ],
#         resize_keyboard=True
#     )




def get_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="Upload a story"))
    keyboard.add(KeyboardButton(text="Read a story"))
    return keyboard.as_markup(resize_keyboard=True)


#admin commands
def keyboardadm() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="Users"))
    keyboard.add(KeyboardButton(text="Stories"))
    return keyboard.as_markup(resize_keyboard=True)


