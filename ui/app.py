import json
import requests

import chainlit as cl

from decouple import config

@cl.on_chat_start
async def start():
    try:
        bot_id = await cl.CopilotFunction(name="url_query_parameter", args={"msg": "bot_id"}).acall()
        rs = requests.get(config("ADMIN_URL")+'/manage/bots/')
        rs.raise_for_status()  # Raises an exception if the request failed
        bots = rs.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return

    if bot_id:
        cl.user_session.set("bot_id", bot_id)
        bot = next((bot for bot in bots if bot.get('id') == bot_id), None)
    else:
        chat_profile = cl.user_session.get("chat_profile")
        bot = next((bot for bot in bots if bot.get('name') == chat_profile), None)

    if bot is None:
        print("Bot not found")
        return

    cl.user_session.set("bot_id", bot.get('id'))
    await cl.Message(content=bot.get('description')).send()

# @cl.on_chat_start
# async def start():
#     bot_id = await cl.CopilotFunction(name="url_query_parameter", args={"msg": "bot_id"}).acall()
#     rs = requests.get(config("ADMIN_URL")+'/manage/bots/')
#     bots = rs.json()

#     if bot_id:
#         cl.user_session.set("bot_id", bot_id)
#         bot = next((bot for bot in bots if bot['id'] == bot_id), None)
#         await cl.Message(content=bot['description']).send()
#     else:
#         chat_profile = cl.user_session.get("chat_profile")
#         bot = next((bot for bot in bots if bot['name'] == chat_profile), None)
#         cl.user_session.set("bot_id", bot['id'])
#         await cl.Message(content=bot['description']).send()

@cl.set_chat_profiles
async def chat_profile():
    rs = requests.get(config("ADMIN_URL")+'/manage/bots/')
    bots = rs.json()

    profiles = []
    for bot in bots:
        profiles.append(
            cl.ChatProfile(
                name=bot['name'],
                markdown_description=bot['description'],
            )
        )
    profiles[0].default = True

    return profiles

@cl.on_message
async def main(message: cl.Message):
    bot_id = cl.user_session.get("bot_id")
    url = config("RETRIEVAL_URL")+'/api/v1/retriever/'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'question': message.content,
        'bot_id': bot_id,
    }

    try:
        response = requests.post(url, headers=headers, data=data)
    except:
        msg = cl.Message(content="")
        answer = "Internal server error. Please try again later or contact the administrator."
        for token in answer:
            await msg.stream_token(token)

        await msg.send()
        return

    if response.status_code == 200:
        rs = response.json()

        answer = rs['data']['response']
        sources = rs['data']['sources']

        text_elements = []

        for index, source in enumerate(sources):
            source_name = f"source {index+1}"
            text_elements.append(
                cl.Text(content=source['text'], name=source_name, display="side")
            )
            
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\n\n\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

        msg = cl.Message(content="", elements=text_elements)
        

        for token in answer:
            await msg.stream_token(token)

        await msg.send()
    else:
        msg = cl.Message(content="")
        answer = "Internal server error. Please try again later or contact the administrator."
        for token in answer:
            await msg.stream_token(token)

        await msg.send()