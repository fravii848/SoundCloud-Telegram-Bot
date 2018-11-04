# -*- coding: utf-8 -*-

import telebot
from time import sleep
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from requests import get as get_web
from json import loads as get_json
from db_class import DB_Worker

get_text = DB_Worker().get_text
bot = telebot.TeleBot("<bot-token>")
app_end = 'client_id=<api-key>'

def check_reg(id):
    try:
        get_text(id, 'good')
    except:
        sleep(2)
        check_reg(id)

def generate_markup3(id, mid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('👍🏼', callback_data=f'yes|{mid}'), InlineKeyboardButton('👎🏼', callback_data=f'no|'))
    
    return markup

def generate_markup2():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    rows = DB_Worker().get_lang()

    for row in rows:
        markup.add(InlineKeyboardButton(row[0], callback_data=f'lang|{row[1]}'))
    
    return markup

def generate_markup(data):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1

    for row in data:
        code = row['stream_url'].replace('https://api.soundcloud.com/tracks/', '')
        code = code.replace('/stream', '')
        markup.add(InlineKeyboardButton(f"({row['user']['username']}) {row['title']}", callback_data=f"music|{code}"))

    return markup

def reply_by_link(message, del_id):
    try:
        if message.text[:23] == 'https://soundcloud.com/' or message.text[:23] == 'http://soundcloud.com/':
            bot.send_chat_action(chat_id=message.chat.id, action='upload_document')
            info = get_json(get_web(f'http://api.soundcloud.com/resolve?url={message.text}&{app_end}').text)
            temp = get_web(info['stream_url'] + '?' + app_end).url

            bot.send_audio(message.chat.id, audio=temp, caption=info['title'])
        else:
            bot.send_message(chat_id=message.chat.id, text=get_text(message.chat.id, 'ulink'))
        
        bot.delete_message(chat_id=message.chat.id, message_id=del_id)
    except:
        pass

def reply_music(id, code, mcode):
    try:
        bot.send_chat_action(chat_id=id, action='upload_document')
        temp = get_web(f'https://api.soundcloud.com/tracks/{code}/stream?{app_end}').url
        temp2 = get_json(get_web(f'https://api.soundcloud.com/tracks/{code}?{app_end}').text)
        bot.send_audio(id, audio=temp, reply_markup=generate_markup3(id, mcode), caption=f"{temp2['user']['username']} - {temp2['title']}")

        del temp, temp2
    except:
        pass

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    step = call.data.split('|', 2)
    id = call.message.chat.id

    if step[0] == "music":
        bot.answer_callback_query(call.id, get_text(id, 'good'))
        reply_music(id, step[1], call.message.message_id)
    elif step[0] == "lang":
        DB_Worker().add_user(id, step[1])
        bot.answer_callback_query(call.id, get_text(id, 'reg_completed'))
    elif step[0] == "yes":
        bot.answer_callback_query(call.id, ';-)')
        bot.clear_step_handler_by_chat_id(id)
        bot.edit_message_reply_markup(chat_id=id, message_id=call.message.message_id, reply_markup=None)
        bot.delete_message(id, step[1])
    elif step[0] == "no":
        bot.answer_callback_query(call.id, ';-(')
        bot.delete_message(id, call.message.message_id)

@bot.message_handler(commands=['start'])
def on_start(m):
    id = m.chat.id

    if DB_Worker().first_seen(id):
        mess = bot.send_message(id, '🇦🇺🇨🇿🇩🇪🇷🇼🇷🇺', reply_markup=generate_markup2())
        check_reg(id)
        bot.delete_message(id, mess.message_id)

    bot.send_message(id, get_text(id, 'start'))

@bot.message_handler(commands=['link'])
def on_link(message):
    mess = bot.send_message(chat_id=message.chat.id, text=get_text(message.chat.id, 'link'), reply_markup=ForceReply())
    bot.register_for_reply(mess, reply_by_link, mess.message_id)

@bot.message_handler()
def command_receive(message):
    id = message.chat.id

    try:
        if len(message.text) >= 4 and 'http' not in message.text:
            a = get_json(get_web(f'https://api.soundcloud.com/tracks?q={message.text}&{app_end}').text)

            if len(a) <= 1:
                bot.send_message(id, get_text(id, 'nfound'))
            else:
                bot.send_message(id, get_text(id, 'smusic'), reply_markup=generate_markup(a))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    bot.polling(none_stop=True)
