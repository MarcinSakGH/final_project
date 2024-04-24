from openai import OpenAI
from decouple import config


def generate_summary(input_text):
    client = OpenAI(api_key=config('OPENAI_KEY'))

    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": """You are a helpful assistant. 
          You always give an answer in English, unless asked otherwise.
          When replying, you are addressing in personal form, directly to the user.
          Take the user's input including the activity's name, duration, description, 
          and emotions associated with it and generate a detailed summary.
          If any negative emotions were experienced in relation to activity, suggest
          what user may do better or how to improve.
          """
        },
        {"role": "user", "content": f"{input_text}"},
    ])

    return response.choices[0].message.content
