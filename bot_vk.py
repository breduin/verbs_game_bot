import logging
from environs import Env
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


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

        return "{}\n".format(response.query_result.fulfillment_text)

def get_dialog_flow_answer(update, context) -> None:
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

    VK_TOKEN = env.str('VK_TOKEN')

    vk_session = vk_api.VkApi(token=VK_TOKEN)

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            print('Новое сообщение:')
            if event.to_me:
                print('Для меня от: ', event.user_id)
            else:
                print('От меня для: ', event.user_id)
            print('Текст:', event.text)


if __name__ == '__main__':
    main()