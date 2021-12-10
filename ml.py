"""Prepare request to and get answer from Google DialogFlow"""
from google.cloud import dialogflow

from environs import Env

env = Env()
env.read_env()
GOOGLE_CLOUD_PROJECT_ID = env.str('GOOGLE_CLOUD_PROJECT_ID')
GOOGLE_CLOUD_PROJECT_LANGUAGE_CODE = env.str(
    'GOOGLE_CLOUD_PROJECT_LANGUAGE_CODE'
    )


def detect_intent_texts(project_id, session_id, texts, language_code):
    """Returns the result of detect intent with texts as inputs."""
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(text=text, 
                                          language_code=language_code
                                          )

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        if response.query_result.intent.is_fallback:
            return None
        else:
            return "{}\n".format(response.query_result.fulfillment_text)


def get_dialog_flow_answer(session_id, texts):
    """Get answer from Google Dialog Flow"""
    
    params = {
        'language_code': GOOGLE_CLOUD_PROJECT_LANGUAGE_CODE,
        'project_id': GOOGLE_CLOUD_PROJECT_ID,
        'session_id': session_id,
        'texts': texts,
    }
    answer = detect_intent_texts(**params)

    return answer
