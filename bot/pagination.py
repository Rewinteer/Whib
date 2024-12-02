from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
    return InlineKeyboardMarkup(buttons)