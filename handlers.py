from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from filters import apply_filter, apply_video_filter
import filetype
from pytube import YouTube
import requests
import os
import yt_dlp
import re
from telegram.error import BadRequest
from telegram import Update
from telegram.ext import CallbackContext

# Start komandasi uchun handler
async def start(update: Update, context: CallbackContext):
    # Clear previous messages
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id

    await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)

    keyboard = [
        [InlineKeyboardButton("Channel 1", url="https://t.me/Kompyuter_service_Termiz")],
        [InlineKeyboardButton("Channel 2", url="https://t.me/Kompyuter_Termizservic")],
        [InlineKeyboardButton("Tasdiqlash", callback_data='confirm_join')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = (
        "Iltimos, quyidagi kanallarga qo'shiling:\n"
        "https://t.me/Kompyuter_service_Termiz\n"
        "https://t.me/Kompyuter_Termizservic\n"
        "Qo'shilganingizdan so'ng, 'Tasdiqlash' tugmasini bosing.\n\n"
        "Bu bot sizga quyidagi xizmatlarni taklif qiladi:\n"
        "- Trenddagi musiqalarni ko'rish va yuklab olish\n"
        "- YouTube videolarini yuklab olish\n"
        "- YouTube videolaridan MP3 fayllarini ajratib olish\n"
        "- Rasmlarni tahrirlash\n"
        "- Videolarni tahrirlash"
    )

    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(message, reply_markup=reply_markup)

# Check if the user has joined the required channels
async def check_membership(user_id, bot):
    channels = ["@Kompyuter_service_Termiz", "@Kompyuter_Termizservic"]
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except BadRequest as e:
            print(f"Error checking membership for channel {channel}: {e.message}")
            return False
    return True

# Confirmation button handler
async def confirm_join(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    bot = context.bot

    if await check_membership(user_id, bot):
        await query.edit_message_text("You have successfully subscribed to the channels. Please send the YouTube video link.")
    else:
        await query.edit_message_text("You have not subscribed to all channels. Please subscribe and try again.")

# Ortga qaytish tugmasi
async def back_to_main_menu(update, context):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# Callback query uchun handler
async def button_callback(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'edit_image':
        await query.edit_message_text("Iltimos, rasmni yuboring.")
        context.user_data['action'] = 'edit_image'
    elif query.data == 'edit_video':
        await query.edit_message_text("Iltimos, videoni yuboring.")
        context.user_data['action'] = 'edit_video'
    elif query.data == 'add_music':
        await show_trending_music(query, context)
    elif query.data == 'upload_video':
        await query.edit_message_text("Iltimos, video linkini yuboring.")
        context.user_data['action'] = 'upload_video'
    elif query.data == 'upload_mp3':
        await query.edit_message_text("Iltimos, MP3 linkini yuboring.")
        context.user_data['action'] = 'upload_mp3'
    elif query.data.startswith('prev_page') or query.data.startswith('next_page'):
        await handle_pagination(query, context)
    elif query.data == 'back_to_main':
        await back_to_main_menu(update, context)
    elif query.data.startswith("music_"):
        await handle_music_selection(update, context)
    elif query.data == 'confirm_join':
        await confirm_join(update, context)

# Sahifalashni boshqarish
async def handle_pagination(query, context):
    current_page = context.user_data.get('music_page', 0)

    if query.data == 'prev_page':
        context.user_data['music_page'] = max(0, current_page - 1)
    elif query.data == 'next_page':
        context.user_data['music_page'] = current_page + 1

    # Yangi sahifani ko'rsatish
    await show_trending_music(query, context)

# Trenddagi musiqalar ro'yxatini ko'rsatish
async def show_trending_music(query, context):
    trending_music = await get_trending_music()  # Musiqalar ro'yxatini olish
    page = context.user_data.get('music_page', 0)  # Joriy sahifani aniqlash
    start_index = page * 10
    end_index = start_index + 10

    keyboard = []
    for music in trending_music[start_index:end_index]:
        keyboard.append([InlineKeyboardButton(music['title'], callback_data=f"music_{music['video_id']}")])

    # Oldingi va keyingi sahifalar tugmalari
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data="prev_page"))
    if end_index < len(trending_music):
        navigation_buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data="next_page"))
    navigation_buttons.append(InlineKeyboardButton("🔙 Ortga", callback_data="back_to_main"))

    keyboard.append(navigation_buttons)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Mashhur musiqalardan birini tanlang:", reply_markup=reply_markup)

# Trenddagi musiqalarni olish
async def get_trending_music():
    # YouTube API kaliti
    YOUTUBE_API_KEY = ''

    # Mashhur videolar ro'yxatini olish
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&chart=mostPopular&regionCode=US&maxResults=40&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    trending_music = []
    for item in data.get('items', []):
        video_id = item['id']
        title = item['snippet']['title']
        trending_music.append({'title': title, 'video_id': video_id})

    return trending_music

# Media (rasm yoki video) qabul qilish uchun handler
async def handle_media(update, context):
    action = context.user_data.get('action')
    file_id = None
    file_path = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_path = 'media/input_image.jpg'
    elif update.message.video:
        file_id = update.message.video.file_id
        file_path = 'media/input_video.mp4'

    if file_id and file_path:
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(file_path)

        # Fayl turini aniqlash
        kind = filetype.guess(file_path)
        if kind is None:
            await update.message.reply_text("Fayl formati aniqlanmadi!")
            return

        if kind.mime.startswith('image') and action == 'edit_image':
            processed_image = apply_filter(file_path, 'enhance')
            await update.message.reply_photo(photo=open(processed_image, 'rb'))
        elif kind.mime.startswith('video') and action == 'edit_video':
            processed_video = apply_video_filter(file_path, 'add_text', text="Salom Dunyo!")
            await update.message.reply_video(video=open(processed_video, 'rb'))

import re

# Function to sanitize file names
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# Progress hook for yt-dlp
def progress_hook(d):
    if d['status'] == 'downloading':
        progress = d['_percent_str']
        eta = d['eta']
        print(f"Downloading: {progress} - ETA: {eta} seconds")

# Video linkni qabul qilish va musiqani ajratish uchun handler
async def handle_youtube_link(update: Update, context: CallbackContext):
    video_url = update.message.text
    video_id = video_url.split("v=")[-1].split("&")[0]  # Extract video ID
    sanitized_video_id = sanitize_filename(video_id)
    context.user_data['selected_video_id'] = sanitized_video_id

    ydl_opts_video = {
        'format': 'bestvideo+bestaudio',
        'outtmpl': f'media/{sanitized_video_id}.mp4',
        'merge_output_format': 'mp4',  # Ensure the output format is mp4
        'progress_hooks': [progress_hook],
    }

    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'outtmpl': f'media/{sanitized_video_id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [progress_hook],
    }

    try:
        # Papkani yaratish
        if not os.path.exists('media'):
            os.makedirs('media')

        # Yuklash va qayta ishlash
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([video_url])

        video_file_path = f"media/{sanitized_video_id}.mp4"
        if os.path.exists(video_file_path):
            await update.message.reply_text("Video yuklandi!")
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_file_path, 'rb'))
        else:
            await update.message.reply_text("Video yuklashda xatolik yuz berdi!")

        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([video_url])

        audio_file_path = f"media/{sanitized_video_id}.mp3"
        if os.path.exists(audio_file_path):
            await update.message.reply_text("Musiqa yuklandi!")
            await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(audio_file_path, 'rb'))
        else:
            await update.message.reply_text("Musiqa yuklashda xatolik yuz berdi!")
    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")

# Qo'shiqni tanlash va yuklash
async def handle_music_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Tanlangan qo'shiqni aniqlash
    if query.data.startswith("music_"):
        video_id = query.data.split("_")[1]  # video_id ni ajratib olish
        sanitized_video_id = sanitize_filename(video_id)
        context.user_data['selected_music_id'] = sanitized_video_id

        # YouTube-dan musiqani yuklash
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'media/{sanitized_video_id}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        try:
            # Papkani yaratish
            if not os.path.exists('media'):
                os.makedirs('media')

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])

            audio_file_path = f"media/{sanitized_video_id}.mp3"

            # Musiqani foydalanuvchiga jo'natish
            if os.path.exists(audio_file_path):
                await query.edit_message_text("Musiqa yuklandi!")
                await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(audio_file_path, 'rb'))
            else:
                await query.edit_message_text("Musiqa yuklashda xatolik yuz berdi!")
        except Exception as e:
            await query.edit_message_text(f"Xatolik yuz berdi: {str(e)}")

