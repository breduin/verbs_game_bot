"""TG bot for Verbs Game Publishing."""
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, CallbackContext
from environs import Env

from dialog_flow import get_dialog_flow_answer
from logs_handlers import TelegramBotHandler


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте\! {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def get_answer(update: Update, context: CallbackContext) -> None:
    """Get answer from DialogFlow and return it to chat."""
    env = Env()
    env.read_env()
    project_id = env.str('GOOGLE_CLOUD_PROJECT_ID')
    language_code = env.str('GOOGLE_CLOUD_PROJECT_LANGUAGE_CODE')

    session_id = update.message.from_user.id
    text = update.message.text

    if answer := get_dialog_flow_answer(session_id,
                                        text,
                                        project_id,
                                        language_code
                                        ):
        update.message.reply_text(answer)


def handle_tg_error(update: Update, context: CallbackContext) -> None:
    """Send message to logger bot"""
    logger.error(msg="TG-bot: Исключение при обработке сообщения:",
                 exc_info=context.error
                 )


def main() -> None:
    """Start the bot."""
    env = Env()
    env.read_env()

    logger.setLevel(logging.INFO)
    bot_handler = TelegramBotHandler(env.str('TG_LOGGER_TOKEN'),
                                     env.str('TG_LOGGING_CHAT_ID')
                                     )
    bot_formatter = logging.Formatter('%(message)s')
    bot_handler.setFormatter(bot_formatter)
    logger.addHandler(bot_handler)

    updater = Updater(env.str('TG_TOKEN'))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, get_answer)
    )
    dispatcher.add_error_handler(handle_tg_error)

    logger.info('TG bot started.')
    try:
        updater.start_polling()
        updater.idle()
    except KeyboardInterrupt:
        logger.info('TG bot stoppped.')
        exit()


if __name__ == '__main__':
    main()
