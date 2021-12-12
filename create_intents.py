"""Create intents for bot.py"""
import json

from environs import Env


def create_intent(project_id,
                  display_name,
                  training_phrases_parts,
                  message_texts):
    """Create an intent of the given intent type."""
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part
            )
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )


def main():

    env = Env()
    env.read_env()

    with open("questions.json", "r") as questions_file:
        intents = json.load(questions_file)

    for intent_name, q_and_a in intents.items():

        questions = q_and_a['questions']
        answers = [q_and_a['answer']]

        create_intent(env.str('GOOGLE_CLOUD_PROJECT_ID'),
                      intent_name, questions,
                      answers
                      )


if __name__ == '__main__':
    main()
