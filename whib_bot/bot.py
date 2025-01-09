import json
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

import api_client, bot_config
import keyboard
from res import strings
from bot_logging_config import logger


MAX_FILE_SIZE = 2097152
ALLOWED_FILE_EXTENSIONS = {'json', 'geojson'}


async def error_handler(update, context):
    logger.error(f'Exception while handling an update - {context.error}')
    await update.message.reply_text(strings.bot_generic_error)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(strings.bot_hello)
    context.user_data.clear()
    tg_chat_id = update.effective_chat.id
    try:
        result = await api_client.create_user(tg_chat_id)
        if result == 400:
            logger.info(f'user with id {tg_chat_id} was not created - already exists')
    except Exception as e:
        await update.message.reply_text(strings.bot_user_creation_error)
        logger.error(f'failed to create a new user with id {tg_chat_id} - {e}')


async def clear_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.delete_message()
    context.user_data.clear()


async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    page = 1
    context.user_data['prompt'] = user_prompt
    context.user_data['page'] = page
    context.user_data['operation'] = handle_prompt.__name__

    try:
        response = await api_client.get_places(user_prompt, page)
        context.user_data['total_pages'] = response['total_pages']
        context.user_data['data'] = response['data']

        await update.message.reply_text(
            strings.bot_choose_option,
            reply_markup=keyboard.get_places_for_prompt_keyboard(
                response['data'],
                1,
                response['total_pages']
            )
        )

    except FileNotFoundError:
        await update.message.reply_text(strings.bot_place_not_found)

    except Exception as e:
        logger.error(f'Failed to process the prompt - {e}')
        await update.message.reply_text(strings.bot_server_error)


async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        query_data = query.data

        if query_data == 'next' and context.user_data['page'] < context.user_data['total_pages']:
            context.user_data['page'] += 1
        elif query_data == 'prev' and context.user_data['page'] > 1:
            context.user_data['page'] -= 1

        page = context.user_data['page']

        if context.user_data['operation'] == handle_prompt.__name__:
            response = await api_client.get_places(context.user_data['prompt'], page)
            reply_markup = keyboard.get_places_for_prompt_keyboard(response['data'], page, context.user_data['total_pages'])
        elif context.user_data['operation'] == unvisited_list.__name__:
            response = await api_client.get_unvisited_districts(context.user_data['tg_chat_id'], page)
            reply_markup = keyboard.get_unvisited_districts_keyboard(response['data'], page, context.user_data['total_pages'])
        else:
            raise FileNotFoundError('empty response')

        context.user_data['data'] = response['data']
        await query.edit_message_reply_markup(reply_markup=reply_markup)

    except Exception as e:
        logger.error(f'failed to paginate data - {e}')


async def handle_place_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        selected_place_id = int(query.data)
        selected_option = None
        for place in context.user_data['data']:
            if place[0] == selected_place_id:
                selected_option = place
                context.user_data['selected_place'] = place
                break

        if selected_option:
            buttons = [
                [
                    InlineKeyboardButton('Так', callback_data='yes'),
                    InlineKeyboardButton('Не', callback_data='no')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(
                strings.you_selected(selected_option[1]),
                reply_markup=reply_markup
            )
        else:
            raise KeyError('cannot find the selected place')

    except Exception as e:
        logger.error(f'failed to send confirmation to the user - {e}')


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query =  update.callback_query
    await query.answer()

    if query.data == 'yes':
        selected_place = context.user_data['selected_place']
        tg_chat_id = update.effective_chat.id
        try:
            await api_client.add_visit(tg_chat_id, selected_place[2])

            await query.edit_message_text(
                strings.selection_confirmed(selected_place[1])
            )
        except Exception:
            await query.edit_message_text(strings.bot_server_error)

    elif query.data == 'no':
        await query.delete_message()

    context.user_data.clear()


async def visits_map_districts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat_id = update.effective_chat.id
    unit_flag = 'District'
    try:
        map_file = await api_client.get_map(tg_chat_id, unit_flag)
        if map_file is None:
            await update.message.reply_text(strings.bot_empty_visits)
            return

        await context.bot.send_photo(
            chat_id=tg_chat_id,
            photo=map_file
        )
    except Exception:
        await update.message.reply_text(strings.bot_generic_error)


async def visits_map_regions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat_id = update.effective_chat.id
    unit_flag = 'Region'
    try:
        map_file = await api_client.get_map(tg_chat_id, unit_flag)
        if map_file is None:
            await update.message.reply_text(strings.bot_empty_visits)
            return

        await context.bot.send_photo(
            chat_id=tg_chat_id,
            photo=map_file
        )
    except Exception:
        await update.message.reply_text(strings.bot_generic_error)


async def handle_attached_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    lat = location.latitude
    lon = location.longitude
    wkt = f'POINT ({lon} {lat})'

    tg_chat_id = update.effective_chat.id

    try:
        await api_client.add_visit(tg_chat_id, wkt)

        await update.message.reply_text(
            strings.location_confirmed(lat, lon)
        )
    except Exception:
        await update.message.reply_text(strings.bot_server_error)


async def unvisited_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat_id = update.effective_chat.id
    page = 1
    context.user_data['page'] = page
    context.user_data['operation'] = unvisited_list.__name__
    context.user_data['tg_chat_id'] = tg_chat_id

    try:
        response = await api_client.get_unvisited_districts(tg_chat_id, page)
        context.user_data['total_pages'] = response['total_pages']
        context.user_data['data'] = response['data']

        await update.message.reply_text(
            strings.bot_unvisited_districts_list,
            reply_markup=keyboard.get_unvisited_districts_keyboard(
                response['data'],
                1,
                response['total_pages']
            )
        )

    except FileNotFoundError:
        await update.message.reply_text(strings.bot_empty_unvisited_districts)

    except Exception as e:
        logger.error(f'Failed to process the prompt - {e}')
        await update.message.reply_text(strings.bot_server_error)


async def handle_selected_unvisited_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return


async def get_random_unvisited_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat_id = update.effective_chat.id
    try:
        random_district = await api_client.get_random_unvisited_district(tg_chat_id)
        await update.message.reply_text(f'Можаш наведаць {random_district} :)')
    except FileNotFoundError:
        await update.message.reply_text(strings.bot_empty_unvisited_districts)
    except Exception as e:
        logger.error(f'failed to get random district - {e}')
        await update.message.reply_text(strings.bot_generic_error)


async def get_visits_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat_id = update.effective_chat.id
    try:
        visits_json = await api_client.get_visits_json(tg_chat_id)
        json_bytes = BytesIO(visits_json.encode('utf-8'))
        json_bytes.name = 'visited_locations.json'
        await context.bot.send_document(tg_chat_id, json_bytes)
    except FileNotFoundError:
        await update.message.reply_text(strings.bot_empty_visits)
    except Exception as e:
        logger.error(f'failed to get visits json - {e}')
        await update.message.reply_text(strings.bot_generic_error)


async def handle_attached_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_chat_id = update.effective_chat.id
    try:
        document = update.message.document
        extension = document.file_name.lower().split('.')[-1]
        if document.file_size > MAX_FILE_SIZE or extension not in ALLOWED_FILE_EXTENSIONS:
            raise AttributeError
        file = await update.message.document.get_file()
        downloaded = await file.download_as_bytearray()
        data = bytearray.decode(downloaded)
        if not data.startswith('{') or not data.endswith('}'):
            raise AttributeError
        await api_client.import_json(tg_chat_id, data)
        await update.message.reply_text(
            strings.bot_geojson_imported
        )
    except (AttributeError, KeyError):
        await update.message.reply_text(
            strings.bot_geojson_wrong_format
        )
    except Exception as e:
        await update.message.reply_text(strings.bot_server_error)


def main():
    application = Application.builder().token(bot_config.WHIB_TOKEN).build()

    application.add_handlers(handlers=[
        CommandHandler('start', start),
        CommandHandler('visits_map_districts', visits_map_districts),
        CommandHandler('visits_map_regions', visits_map_regions),
        CommandHandler('unvisited_list', unvisited_list),
        CommandHandler('random_unvisited_district', get_random_unvisited_district),
        CommandHandler('visits_json', get_visits_json),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt),
        MessageHandler(filters.LOCATION & ~filters.COMMAND, handle_attached_location),
        MessageHandler(filters.ATTACHMENT & ~filters.COMMAND, handle_attached_json),
        CallbackQueryHandler(handle_pagination, pattern='^(next|prev)$'),
        CallbackQueryHandler(handle_place_selection, pattern='^[0-9]+$'),
        CallbackQueryHandler(handle_confirmation, pattern='^(yes|no)$'),
        CallbackQueryHandler(clear_message, pattern='^(discard|close)$'),
        CallbackQueryHandler(handle_selected_unvisited_place, pattern='\D+$'),
    ])
    application.add_error_handler(error_handler)

    logger.info("Bot is starting")
    application.run_polling()

if __name__ == '__main__':
    main()