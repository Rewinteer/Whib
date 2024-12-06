from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from res import strings


def add_service_buttons(buttons, page, total_pages):
    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton('<-', callback_data='prev'))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton('->', callback_data='next'))
    if navigation_buttons:
        buttons.append(navigation_buttons)
    return buttons


def get_places_for_prompt_keyboard(data, page, total_pages):
    buttons = [
        [InlineKeyboardButton(text=place[1], callback_data=str(place[0]))]
        for place in data
    ]
    add_service_buttons(buttons, page, total_pages)
    discard_button = [InlineKeyboardButton(strings.bot_discard_button, callback_data='discard')]
    buttons.append(discard_button)
    return InlineKeyboardMarkup(buttons)


def get_unvisited_districts_keyboard(data, page, total_pages):
    buttons = [
        [InlineKeyboardButton(text=district, callback_data=district)]
        for district in data
    ]
    add_service_buttons(buttons, page, total_pages)
    close_button = [InlineKeyboardButton(strings.bot_close_button, callback_data='close')]
    buttons.append(close_button)
    return InlineKeyboardMarkup(buttons)