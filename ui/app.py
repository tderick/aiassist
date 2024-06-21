import requests

import chainlit as cl

from decouple import config



@cl.on_chat_start
async def start():
    bot_id = await cl.CopilotFunction(name="url_query_parameter", args={"msg": "bot_id"}).acall()
    if bot_id:
        cl.user_session.set("bot_id", bot_id)

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