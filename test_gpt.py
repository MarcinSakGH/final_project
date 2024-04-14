import os
from decouple import config

from openai import OpenAI

client = OpenAI(api_key=config('OPENAI_KEY'))


completion = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': 'Write me essay about bears'}
])
print(completion.choices[0].message)
