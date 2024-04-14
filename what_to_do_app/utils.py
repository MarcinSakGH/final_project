from openai import OpenAI
from decouple import config



def generate_summary(input_text):
    client = OpenAI(api_key=config('OPENAI_KEY'))

    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": f"{input_text}"},
    ])

    return response.choices[0].message.content
