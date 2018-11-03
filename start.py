# -*- coding: utf-8 -*-

import telebot
from telebot import types
from requests import get as get_web
from json import loads as get_json

bot = telebot.TeleBot("<bot-token>")
app_end = 'client_id=<api-key>'

def reply_by_link(message, del_id):
    try:
        if message.text[:23] == 'https://soundcloud.com/' or message.text[:23] == 'http://soundcloud.com/':
            bot.send_chat_action(chat_id=message.chat.id, action='upload_document')
            info = get_json(get_web('http://api.soundcloud.com/resolve?url=' + message.text + '&' + app_end).text)
            temp = get_web(info['stream_url'] + '?' + app_end).url

            bot.send_audio(message.chat.id, audio=temp, caption=info['title'])
        else:
            bot.send_message(chat_id=message.chat.id, text='This link is not supported.')
        
        bot.delete_message(chat_id=message.chat.id, message_id=del_id)
    except Exception as e:
        open('errors_list.txt', 'a', encoding='utf-8').write(e + '\n')
        bot.send_message(message.chat.id, "Error in request. Try later.")

def reply_music(message, arr, del_id):
    try:
        info = arr[int(message.text)]
        bot.send_chat_action(chat_id=message.chat.id, action='upload_document')
        temp = get_web(info['link'] + '?' + app_end).url
        bot.send_audio(message.chat.id, audio=temp, caption=info['name'])

        del temp, info
    except Exception as e:
        open('errors_list.txt', 'a', encoding='utf-8').write(e + '\n')
        bot.send_message(message.chat.id, "Error in request. Try later.")
    
    bot.delete_message(chat_id=message.chat.id, message_id=del_id)

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

@bot.message_handler(commands=['link'])
def on_link(message):
    mess = bot.send_message(chat_id=message.chat.id, text='Send link to me', reply_markup=types.ForceReply())
    bot.register_for_reply(mess, reply_by_link, mess.message_id)

@bot.message_handler()
def command_receive(message):
    try:
        if len(message.text) >= 4 and 'http' not in message.text:
            a = get_web('https://api.soundcloud.com/tracks?q={}&{}'.format(message.text, app_end)).text
            b = get_json(a)

            if len(b) <= 1:
                bot.send_message(message.chat.id, "Not found.")
            else:
                temp = create_dict(b)
                mess = bot.send_message(chat_id=message.chat.id, text=create_text(temp), reply_markup=types.ForceReply())
                bot.register_for_reply(mess, reply_music, temp, mess.message_id)
    except Exception as e:
        open('errors_list.txt', 'a', encoding='utf-8').write(e + '\n')
        bot.send_message(message.chat.id, "Opppsss... Something wrong.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
