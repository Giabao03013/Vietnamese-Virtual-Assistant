import requests
import speech_recognition as sr
import subprocess
from gtts import gTTS
import pyttsx3
import playsound
import os
import Get_time

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty("voice",voices[1].id)
    newVoiceRate = 130
    engine.setProperty('rate', newVoiceRate)
    engine.say(text)
    engine.runAndWait()


def reponse(message):
    bot_message = ""
    while bot_message != 'Bye bye':
        r = requests.post('http://localhost:5002/webhooks/rest/webhook', json={"message": message})
        for i in r.json():
            bot_message += i['text'] + '\n'
        return bot_message

def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source)
            text = r.recognize_google(audio, language='vi-VI')
        except:
            msg = "Tôi không nghe rõ bạn nói lắm. Bạn có thể nói lại dùm tui được không vậy?"
            print(msg)
#
