"""VK bot for Verbs Game Publishing."""
import logging
import random
import requests
import vk_api

from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from dialog_flow import get_dialog_flow_answer
from logs_handlers import TelegramBotHandler


logger = logging.getLogger(__name__)


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

    vk_session = vk_api.VkApi(token=env.str('VK_TOKEN'))

    vk_session_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.info('VK bot started.')

    max_int32_number = 2_147_483_647

    while True:
        try:
            for event in longpoll.listen():
                if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
                    continue
                message = event.text
                try:
                    answer = get_dialog_flow_answer(
                        event.user_id,
                        message,
                        env.str('GOOGLE_CLOUD_PROJECT_ID'),
                        env.str('GOOGLE_CLOUD_PROJECT_LANGUAGE_CODE')
                        )
                except Exception as e:
                    logger.error('DialogFlow error.')
                    logger.exception(e)
                    continue
                if not answer:
                    continue
                vk_session_api.messages.send(user_id=event.user_id,
                                             message=answer,
                                             random_id=random.randint(
                                                 1, max_int32_number
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
