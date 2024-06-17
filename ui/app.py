import requests

import chainlit as cl


@cl.on_chat_start
async def start():
    pass

@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    url = 'http://127.0.0.1:8001/api/v1/retriever/'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'question': message.content,
        'bot_id': 'unipi',
    }

    response = requests.post(url, headers=headers, data=data)
    # Send a response back to the user
    await cl.Message(
        content=response.json()['response'],
    ).send()