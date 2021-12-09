import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from environs import Env


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

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


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def detect_intent_texts(project_id, session_id, texts, language_code):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""
    from google.cloud import dialogflow

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        # print("=" * 20)
        # print("Query text: {}".format(response.query_result.query_text))
        # print(
        #     "Detected intent: {} (confidence: {})\n".format(
        #         response.query_result.intent.display_name,
        #         response.query_result.intent_detection_confidence,
        #     )
        # )
        # print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))
        return "{}\n".format(response.query_result.fulfillment_text)

def get_dialog_flow_answer(update: Update, context: CallbackContext) -> None:
    """Get answer via Google Dialog Flow"""
    env = Env()
    env.read_env()
    GOOGLE_CLOUD_PROJECT_ID = env.str('GOOGLE_CLOUD_PROJECT_ID')
    GOOGLE_CLOUD_PROJECT_LANGUAGE_CODE = env.str('GOOGLE_CLOUD_PROJECT_LANGUAGE_CODE')
    
    params = {
        'language_code': GOOGLE_CLOUD_PROJECT_LANGUAGE_CODE,
        'project_id': GOOGLE_CLOUD_PROJECT_ID,
        'session_id': update.message.from_user.id,
        'texts': [update.message.text],
    }
    logger.info(params)
    answer = detect_intent_texts(**params)
    logger.info(answer)
    update.message.reply_text(answer)


def main() -> None:
    """Start the bot."""
    env = Env()
    env.read_env()

    TG_TOKEN = env.str('TG_TOKEN')

    updater = Updater(TG_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, get_dialog_flow_answer))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()