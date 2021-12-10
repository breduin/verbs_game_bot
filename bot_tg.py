import logging
import telegram

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, CallbackContext
from environs import Env

from ml import get_dialog_flow_answer


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте\! {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def get_answer(update: Update, context: CallbackContext) -> None:
    """Get answer from DialogFlow and return it to chat."""
    session_id = update.message.from_user.id
    texts = [update.message.text]

    answer = get_dialog_flow_answer(session_id, texts)
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

    TG_LOGGER_TOKEN = env.str('TG_LOGGER_TOKEN')
    TG_LOGGING_CHAT_ID = env.str('TG_LOGGING_CHAT_ID')
    logging_bot = telegram.Bot(token=TG_LOGGER_TOKEN)

    class BotHandler(logging.Handler):

        def emit(self, record):
            log_entry = self.format(record)
            logging_bot.send_message(chat_id=TG_LOGGING_CHAT_ID,
                                     text=log_entry
                                     )

    logger.setLevel(logging.INFO)
    bot_handler = BotHandler()
    bot_formatter = logging.Formatter('%(message)s')
    bot_handler.setFormatter(bot_formatter)
    logger.addHandler(bot_handler)

    TG_TOKEN = env.str('TG_TOKEN')

    updater = Updater(TG_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, get_answer
        )
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
