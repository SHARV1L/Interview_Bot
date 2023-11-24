from fastapi import FastAPI, UploadFile
from dotenv import load_dotenv 

import openai
import os
import json

load_dotenv()  # take environment variables from .env

openai.api_key = os.getenv("OPEN_API_KEY")
openai.organization = os.getenv("OPEN_AI_ORG")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "This is the starting page, thankyou for visiting"}

@app.post("/talk")
async def post_audio(file: UploadFile):
    user_message = transcribe_audio(file)
    chat_response = get_chat_response(user_message)

# Creating functions to make the code modular

def transcribe_audio(file):
    #audio_file= open(file.filename, "rb")
    #transcript = openai.Audio.transcribe("whisper-1", audio_file)
    transcript = {"role": "user", "content": "Who won the world series in 2020?"}
    print(transcript)
    #return{"message": "Hey, your audio has been transcribed"}
    return transcript

def get_chat_response(user_message):
    messages = load_messages()
    messages.append(user_message)

    # Now we can send the request to chat GPT with older messages 
    gpt_response = {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."}

    # Here we will save the messages
    save_messages(user_message, gpt_response)


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
            {"role": "system", "content": "You are interviewing the user for the Data Analyst position. Ask them relevent question and provide them with feedback for their response and help them with their preperation. You are Voxel and the user is Sharvil. Provide good and brief response and try be be funny and engaging. "}
        )          
    return messages

def save_messages (user_message, gpt_response):
    file = 'database.json'
    messages = load_messages()
    messages.append(user_message)
    messages.append(gpt_response)
    with open(file, 'w') as f:
        json.dump(messages, f)


#1 Send audio and have it transcribed


#2 Send a request to ChatGPT and get a response


#3 Save the chat history 
