from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, \
    MessageHandler, filters

import api_client
import pagination
import res.strings as strings
from bot_logging_config import logger
from config import bot_config

HANDLE_PROMPT, SHOW_PLACES, CONFIRM = range(3)

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
    return 'HELLO'


async def clear_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()


async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    page = 1
    context.user_data['prompt'] = user_prompt
    context.user_data['page'] = page

    try:
        response = await api_client.get_places(user_prompt, page)
        context.user_data['total_pages'] = response['total_pages']
        context.user_data['data'] = response['data']

        await update.message.reply_text(
            strings.bot_choose_option,
            reply_markup=pagination.get_keyboard(
                response['data'],
                1,
                response['total_pages']
            )
        )
        return HANDLE_PROMPT

    except FileNotFoundError as e:
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
        response = await api_client.get_places(context.user_data['prompt'], page)
        context.user_data['data'] = response['data']

        await query.edit_message_reply_markup(
            reply_markup=pagination.get_keyboard(response['data'], page, context.user_data['total_pages'])
        )
        return SHOW_PLACES
    except Exception as e:
        logger.error(f'failed to paginate data - {e}')


async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        return CONFIRM

    except Exception as e:
        logger.error(f'failed to send confirmation to the user - {e}')


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query =  update.callback_query
    await query.answer()

    logger.debug('Confirmation handler is triggered')

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
    return CONFIRM


def main():
    application = Application.builder().token(bot_config.WHIB_TOKEN).build()

    place_selection_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt),],
        states={
            HANDLE_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt)],
            SHOW_PLACES: [
                CallbackQueryHandler(handle_pagination, pattern="^(next|prev)$"),
                CallbackQueryHandler(handle_selection, pattern="^[0-9]+$"),
            ],
            CONFIRM: [CallbackQueryHandler(handle_confirmation, pattern="^(yes|no)$")],
        },
        fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, clear_context)]
    )


    application.add_handler(CommandHandler('start', start))
    application.add_handler(place_selection_handler)
    application.add_error_handler(error_handler)

    logger.info("Bot is starting")
    application.run_polling()

if __name__ == '__main__':
    main()