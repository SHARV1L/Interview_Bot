from fastapi import FastAPI, UploadFile
from dotenv import load_dotenv 
from fastapi.responses import StreamingResponse

import openai
import os
import json
import requests

load_dotenv()  # take environment variables from .env

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_API_ORG")
elevenlabs_key = os.getenv("ELEVENLABS_KEY")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "This is the starting page, thankyou for visiting"}

@app.post("/talk")
async def post_audio(file: UploadFile):
    user_message = transcribe_audio(file)
    chat_response = get_chat_response(user_message)
    audio_output = text_to_speech(chat_response)

    def iterfile():  
        yield audio_output
    return StreamingResponse(iterfile(), media_type="video/mpeg")

# Creating functions to make the code modular

def transcribe_audio(file):
    audio_file= open(file.filename, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript)
    return transcript

def get_chat_response(user_message):
    messages = load_messages()
    messages.append({"role": "user", "content": user_message['text']})
    #messages.append(user_message)
    print(messages)

    # Sending the request to ChatGPT:
    gpt_response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages
        )
    
    parsed_gpt_response = gpt_response['choices'][0] ['message'] ['content']

    # Here we will save the messages
    save_messages(user_message['text'], parsed_gpt_response)

    return parsed_gpt_response


def load_messages():
    messages = []
    file = 'database.json'

    # Checking if file is empty: if yes, we add the content
    empty = os.stat(file).st_size == 0

    # If file not empty, loop through history and add to messages
    if not empty:
        with open(file) as db_file:
            data = json.load(db_file)
            for item in data:
                messages.append(item)
    else:
        messages.append(
            {"role": "system", "content": "You are helping the user to prepare for the Data Analyst role in a company. Ask them relevent question and provide them with feedback for their response thereby helping them with their preperation. You are Greg and the user is Sharvil. Provide accurate and brief responses and try being be funny and engaging. "}
        )          
    return messages

def save_messages (user_message, gpt_response):
    file = 'database.json'
    messages = load_messages()
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": gpt_response})
    with open(file, 'w') as f:
        json.dump(messages, f)


def text_to_speech(text):
    voice_id = "CYw3kZ02Hs0563khs1Fj"

    body = {
        "model_id": "eleven_monolingual_v2",
        "text": text,
        "voice_settings": {
            "similarity_boost": 0,
            "stability": 0,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }            

    headers = {
        "Content-Type": "application/json",
        "accept": "audio/mpeg",
        "xi-api-key": elevenlabs_key
    }

    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    try: 
        response = requests.post(url, json = body, headers = headers)
        if (response.status_code == 200):
            return response.content
        else:
            print("Something went wrong")
    except Exception as e:
        print(e)
    

#1 Send audio and have it transcribed


#2 Send a request to ChatGPT and get a response


#3 Save the chat history 
