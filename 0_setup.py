from openai import OpenAI
from demo_util import color
import os
import sys
from dotenv import load_dotenv

load_dotenv()
openai_key =os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_key)

# === Demo Loop ===

model = "gpt-4o-mini"
system_message = "You are a helpful Assistant."

messages = []
while True:
    # get user input
    user = input(color("User: ", "blue") + "\033[90m")
    messages.append({"role": "user", "content": user})

    # get model completion
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_message}] + messages,
    )
    message = response.choices[0].message
    print(color("Assistant:", "yellow"), message.content)

    # add message to history
    messages.append(message)
