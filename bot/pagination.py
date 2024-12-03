from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import res.strings as strings

def get_keyboard(data, page, total_pages):
    buttons = [
        [InlineKeyboardButton(text=place[1], callback_data=str(place[0]))]
        for place in data
    ]
    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton('<-', callback_data='prev'))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton('->', callback_data='next'))
    if navigation_buttons:
        buttons.append(navigation_buttons)
    discard_button = [InlineKeyboardButton(strings.bot_discard_button, callback_data='discard')]
    buttons.append(discard_button)
    return InlineKeyboardMarkup(buttons)