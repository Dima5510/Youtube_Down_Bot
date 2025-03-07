from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from handlers import start, button_callback, back_to_main_menu, handle_youtube_link
from filters import apply_filter, apply_video_filter

# Botni ishga tushirish
TOKEN = ''

def get_trending_music():
    # Dummy implementation for retrieving trending music
    # Replace with actual logic as needed
    return ['music1.mp3', 'music2.mp3', 'music3.mp3', 'music4.mp3', 'music5.mp3']

async def handle_media(update, context):
    file_id = update.message.photo[-1].file_id if update.message.photo else update.message.video.file_id
    file = await context.bot.get_file(file_id)
    await file.download('input/input_file.jpg')
    action = context.user_data.get('action')
    if action == 'edit_image':
        processed_image = apply_filter('input/input_file.jpg', 'enhance')
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(processed_image, 'rb'))
    elif action == 'edit_video':
        processed_video = apply_video_filter('input/input_file.mp4', 'add_text', text="Salom Dunyo!")
        context.bot.send_video(chat_id=update.effective_chat.id, video=open(processed_video, 'rb'))
    elif action == 'add_music':
        # Trenddagi musiqalarni olish
        trending_music = get_trending_music()
        context.user_data['trending_music'] = trending_music
        context.user_data['current_page'] = 0
        context.user_data['total_pages'] = len(trending_music) // 5 + (len(trending_music) % 5 > 0)
        await show_trending_music(update, context)

async def show_trending_music(update, context):
    trending_music = context.user_data.get('trending_music', [])
    current_page = context.user_data.get('current_page', 0)
    start_index = current_page * 5
    end_index = start_index + 5
    page_music = trending_music[start_index:end_index]
    message = "Trending Music:\n" + "\n".join(page_music)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main():
    application = Application.builder().token(TOKEN).build()

    # Komandalar va handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_link))
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^back_to_main$"))

    application.run_polling()

if __name__ == "__main__":
    main()