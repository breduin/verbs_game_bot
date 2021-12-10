import logging
import random
import requests
import telegram
import vk_api

from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from ml import get_dialog_flow_answer


logger = logging.getLogger(__name__)


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

    logger.setLevel(logging.DEBUG)
    bot_handler = BotHandler()
    bot_formatter = logging.Formatter('%(message)s')
    bot_handler.setFormatter(bot_formatter)
    logger.addHandler(bot_handler)

    VK_TOKEN = env.str('VK_TOKEN')
    vk_session = vk_api.VkApi(token=VK_TOKEN)

    vk_session_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.info('VK bot started.')

    while True:
        try:
            for event in longpoll.listen():
                if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
                    continue
                message = [event.text]
                try:
                    answer = get_dialog_flow_answer(event.user_id, message)
                except Exception as e:
                    logger.error('DialogFlow error.')
                    logger.exception(e)
                    continue
                if not answer:
                    continue
                vk_session_api.messages.send(user_id=event.user_id,
                                             message=answer,
                                             random_id=random.randint(
                                                 1, 2_147_483_647
                                                 )
                                             )
        except requests.exceptions.ReadTimeout:
            continue
        except KeyboardInterrupt:
            logger.info('VK bot stoppped.')
            exit()
        except Exception as e:
            logger.error('VK-bot: error.')
            logger.exception(e)
            raise e


if __name__ == '__main__':
    main()
