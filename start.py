# -*- coding: utf-8 -*-

import telebot
from telebot import types
from requests import get as get_web
from json import loads as get_json

bot = telebot.TeleBot("<bot-token>")
app_end = 'client_id=<api-key>'

def reply_music(message, arr):
    try:
        info = arr[int(message.text)]
        temp = get_web(info['link'] + '?' + app_end).url
        bot.send_audio(message.chat.id, audio=temp, caption=info['name'])

        del temp, info
    except:
        bot.send_message(message.chat.id, "Error in request. Try later.")

def create_text(rows):
    text = ''

    for i in range(len(rows)):
        i += 1
        text += '{}. {}\n'.format(i, rows[i]['name'])

    text += '\nSend number of sound.'

    return text

def create_dict(rows):
    i = 0
    temp = {}

    for row in rows:
        i += 1

        temp[i] = {}
        temp[i]['name'] = row['title']
        temp[i]['link'] = row['stream_url']
    
    return temp

@bot.message_handler(commands=['start'])
def on_start(message):
    bot.send_message(message.chat.id, "Hello. Send name of sound to me and get file.")

@bot.message_handler()
def command_receive(message):
    if len(message.text) >= 4:
        a = get_web('https://api.soundcloud.com/tracks?q={}&{}'.format(message.text, app_end)).text
        b = get_json(a)

        if len(b) <= 1:
            bot.send_message(message.chat.id, "Not found.")
        else:
            temp = create_dict(b)
            mess = bot.send_message(message.chat.id, create_text(temp), reply_markup=types.ForceReply())
            bot.register_for_reply(mess, reply_music, temp)

if __name__ == "__main__":
    bot.polling(none_stop=True)
