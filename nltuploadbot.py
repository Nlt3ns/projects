import re
import io
import time
import requests
import random
import json
import telegram
import cloudinary
import signal
import csv
import os
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram.ext import Updater


TOKEN = '6181562042:AAGovDYdrkHUaQtFBNgpjqlqZQbDLhG7-Is'
CHANNEL_ID = '-1001899617932'

cloudinary.config(
cloud_name = "dzwttrqks",
api_key = "941398376366348",
api_secret = "84wx86PpoeABcq8KGUV2CvQ-axw",
secure = True
)



bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

def handle_inline_button(update: telegram.Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    message_id = query.message.message_id
    chat_id = query.message.chat_id
    data = query.data

    # Get user's previous reaction
    previous_reaction = context.user_data.get(f"{message_id}_{user_id}")

    # Check if user has already reacted with the same type of reaction
    if data == 'like':
        reaction = '❤️'
        opposite_reaction = '💔'
    elif data == 'dislike':
        reaction = '💔'
        opposite_reaction = '❤️'

    if previous_reaction == reaction:
        query.answer(text="You have already reacted with the same reaction.")
        return


    # Update reaction count
    like_count = context.chat_data.get(f"{message_id}_like", 0)
    dislike_count = context.chat_data.get(f"{message_id}_dislike", 0)
    if previous_reaction == opposite_reaction:
        if opposite_reaction == '❤️':
            like_count -= 1
        elif opposite_reaction == '💔':
            dislike_count -= 1
    if data == 'like':
        like_count += 1
        if previous_reaction == opposite_reaction:
            context.chat_data[f"{message_id}_dislike"] = dislike_count
        context.chat_data[f"{message_id}_like"] = like_count
    elif data == 'dislike':
        dislike_count += 1
        if previous_reaction == opposite_reaction:
            context.chat_data[f"{message_id}_like"] = like_count
        context.chat_data[f"{message_id}_dislike"] = dislike_count


    # Save user reaction
    context.user_data[f"{message_id}_{user_id}"] = reaction

    # Update Inline button with new reaction count
    inline_keyboard = [[InlineKeyboardButton(f"❤️ {like_count}", callback_data='like'), InlineKeyboardButton(f"💔 {dislike_count}", callback_data='dislike')], [InlineKeyboardButton(button_text, url=button_url)],[InlineKeyboardButton(button_text_store, url=button_store_url)]]
    query.edit_message_reply_markup(InlineKeyboardMarkup(inline_keyboard))

    # Send confirmation message to user
    query.answer(text=f"You reacted with '{reaction}'. Thanks for your feedback!")


dispatcher.add_handler(CallbackQueryHandler(handle_inline_button))

# Start the Telegram bot
updater.start_polling()
print('Bot started.')




last_pub_date = None

while True:
    response = requests.get('https://nudeleaksteens.com/feed?swcfpc=1')
    soup = BeautifulSoup(response.content, 'xml')
    item = soup.find('item')
    pub_date = item.find('pubDate').text.strip()

    if pub_date != last_pub_date:
        # Un nouvel article a été publié, extraire les informations et envoyer le message Telegram
        last_pub_date = pub_date


        response = requests.get('https://nudeleaksteens.com/?swcfpc=1')
        soup = BeautifulSoup(response.content, 'html.parser')
        image_url = soup.find('span', {'data-src': True})['data-src']

        response = requests.get('https://nudeleaksteens.com/feed?swcfpc=1')
        soup = BeautifulSoup(response.content, 'xml')
        item = soup.find('item')
        title = item.find('title').text.strip()

        response = requests.get('https://nudeleaksteens.com/feed?swcfpc=1')
        soup = BeautifulSoup(response.content, 'xml')
        item = soup.find('item')
        title = item.find('title').text.strip()
        content_encoded = item.find('content:encoded').text.strip()
        soup_encoded = BeautifulSoup(content_encoded, 'html.parser')
        strong_tag = soup_encoded.find('strong')
        desc = 'This album contains <b>' + strong_tag.text.strip() + '</b>'

        public_id = 'model' + str(random.randint(1000000, 9999999))

        upload(image_url, public_id=public_id)

        response = requests.get('https://nudeleaksteens.com/feed?swcfpc=1')
        soup = BeautifulSoup(response.content, 'xml')
        item = soup.find('item')
        button_url = item.find('link').text.strip()

        # Generate signed URL with Cloudinary, crop left half of the image
        url, options = cloudinary_url(public_id, gravity="west", height=1000, width=650, crop="fill")

        button1_text = "❤️"
        button1_callback = "like"
        button2_text = "💔"
        button2_callback = "dislike"
        like_count = 0
        dislike_count = 0

        button_text = "HER NUDES"
        button_url = button_url
        button_text_store = "💠STORE💠"
        button_store_url = "https://nudeleaksteens.com/products?swcfpc=1"


        # Créer le bouton Inline
        inline_keyboard = [[InlineKeyboardButton(f"{button1_text} {like_count}", callback_data=button1_callback), InlineKeyboardButton(f"{button2_text} {dislike_count}", callback_data=button2_callback)], [InlineKeyboardButton(button_text, url=button_url)],[InlineKeyboardButton(button_text_store, url=button_store_url)]]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)

        # Initialize post_id variable
        post_id = None

        bot = telegram.Bot(token=TOKEN)

        # Send the message with the Inline button attached
        caption = f"New NLT - {title} 💜\n\n{desc}\n<a href='{url}'>\u200B</a>"
        message = bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode='HTML', disable_web_page_preview=False, reply_markup=reply_markup)

        # Update the post_id variable with the ID of the message
        post_id = message.message_id


    time.sleep(30)