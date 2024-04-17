from openai import OpenAI
from decouple import config


api_key = config('OPENAI_KEY')
openai = OpenAI(api_key=api_key)

messages = []
system_msg = input('What type of chatbot would you like me to be:\n')
messages.append({"role": "system", "content": system_msg})

print("Your new assistant is ready!")
while input != "quit()":
    message = input()
    messages.append({"role": "user", "content": message})
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=messages)
    reply = response.choices[0].message.content
    messages.append({"role": "user", "content": reply})
    print("\n" + reply + "\n")