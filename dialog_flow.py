"""Prepare request to and get answer from Google DialogFlow."""
from google.cloud import dialogflow

from environs import Env


def get_dialog_flow_answer(session_id, text):
    """Get answer from Google Dialog Flow"""
    env = Env()
    env.read_env()
    project_id = env.str('GOOGLE_CLOUD_PROJECT_ID')
    language_code = env.str('GOOGLE_CLOUD_PROJECT_LANGUAGE_CODE')

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text,
                                      language_code=language_code
                                      )

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session,
                 "query_input": query_input
                 }
    )
    if response.query_result.intent.is_fallback:
        return None

    return response.query_result.fulfillment_text
