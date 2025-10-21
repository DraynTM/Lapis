import telebot
from telebot import types
import yt_dlp
import os
import json
import requests

TELEGRAM_BOT_TOKEN = "7910601244:AAHTge82EbZ50jQ1wkLo1hP5_jlhwMZckic"
DEFAULT_DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "YouTube Downloads")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

VIDEO_FORMATS = ['mp4', 'mkv', 'avi', 'mov']
AUDIO_FORMATS = ['mp3', 'flac', 'aac', 'wav']

user_settings = {}
user_states = {}
user_data = {}

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def load_user_settings():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}


def save_user_settings():
    with open(CONFIG_FILE, 'w') as file:
        json.dump(user_settings, file)


def set_user_state(user_id, state):
    user_states[user_id] = state


def get_user_state(user_id):
    return user_states.get(user_id, None)


def get_user_setting(user_id, key):
    user_id_str = str(user_id)
    if user_id_str not in user_settings:
        default = {
            'download_folder': DEFAULT_DOWNLOAD_FOLDER,
            'audio_format': AUDIO_FORMATS[0],
            'video_format': VIDEO_FORMATS[0]
        }
        user_settings[user_id_str] = default
        save_user_settings()
    return user_settings[user_id_str].get(key, None)


def update_user_setting(user_id, key, value):
    user_id_str = str(user_id)
    user_settings[user_id_str][key] = value
    save_user_settings()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if str(user_id) not in user_settings:
        user_settings[str(user_id)] = {
            'download_folder': DEFAULT_DOWNLOAD_FOLDER,
            'audio_format': AUDIO_FORMATS[0],
            'video_format': VIDEO_FORMATS[0]
        }
        save_user_settings()
    main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu.add("Скачать", "Настройки")
    main_menu.add("О программе")
    bot.send_message(message.chat.id, "Приветик, солнышко :3\nЧто ты хочешь сделать? >w<", reply_markup=main_menu)


@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    text = message.text
    user_id = message.from_user.id
    if text == "Скачать":
        bot.send_message(message.chat.id, "Пожалуйста, вставь ссылочку на видео из ютубчика:")
        set_user_state(user_id, "awaiting_url")
    elif text == "Настройки":
        settings_menu(message)
    elif text == "О программе":
        about(message)
    elif text == "Назад":
        start(message)


@bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == "awaiting_url")
def handle_url(message):
    user_id = message.from_user.id
    video_url = message.text
    if video_url.lower() in ['exit', 'quit', 'q']:
        set_user_state(user_id, None)
        bot.send_message(message.chat.id, "Ухожу в сон...")
        return
    user_data[user_id] = {'url': video_url}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Видео", callback_data='format_video'))
    markup.add(types.InlineKeyboardButton("Аудио", callback_data='format_audio'))
    bot.send_message(message.chat.id, "Какой форматик хочешь скачать? :3", reply_markup=markup)
    set_user_state(user_id, "awaiting_format")


@bot.callback_query_handler(func=lambda call: True)
def handle_format_callback(call):
    user_id = call.from_user.id
    data = call.data
    if data.startswith('format_'):
        download_type = '1' if data == 'format_video' else '2'
        video_url = user_data[user_id]['url']
        download_media_telegram(video_url, download_type, user_id, call.message.chat.id)
        set_user_state(user_id, None)
        user_data.pop(user_id, None)
        bot.answer_callback_query(call.id, "Скачивание запущено")


def download_media_telegram(video_url, download_type, user_id, chat_id):
    download_folder = get_user_setting(user_id, 'download_folder')
    audio_format = get_user_setting(user_id, 'audio_format')
    video_format = get_user_setting(user_id, 'video_format')

    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
    os.makedirs(download_folder, exist_ok=True)

    ydl_opts = {}
    if download_type == '2':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
            }],
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        }
    else:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': video_format,
            }],
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info.get('title', 'Видео')
            send_telegram_notification(video_title, video_url, chat_id)
            bot.send_message(chat_id, f"Скачивание завершено! Файл '{video_title}' успешно скачан!")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")


def send_telegram_notification(video_title, video_url, chat_id):
    message = (
        f"🔔 Новое скачивание:\n"
        f"🎬 Видео: {video_title}\n"
        f"🔗 Ссылка: {video_url}"
    )
    bot.send_message(chat_id, message)


@bot.message_handler(func=lambda m: m.text == "Настройки")
def settings_menu(message):
    settings_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    settings_markup.add("Указать путь", "Выбрать форматы")
    settings_markup.add("Назад")
    bot.send_message(message.chat.id, "Настройки:", reply_markup=settings_markup)


@bot.message_handler(func=lambda m: m.text == "Указать путь")
def set_path(message):
    bot.send_message(message.chat.id, "Введи новый путь для сохранения файлов:")
    set_user_state(message.from_user.id, "awaiting_path")


@bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == "awaiting_path")
def handle_path(message):
    user_id = message.from_user.id
    new_path = message.text.strip()
    update_user_setting(user_id, 'download_folder', new_path)
    bot.send_message(message.chat.id, f"Путь обновлен: {new_path}")
    set_user_state(user_id, None)


@bot.message_handler(func=lambda m: m.text == "Выбрать форматы")
def choose_formats(message):
    current_video = get_user_setting(message.from_user.id, 'video_format')
    current_audio = get_user_setting(message.from_user.id, 'audio_format')
    bot.send_message(message.chat.id, f"Текущие форматы:\n"
                                      f"Видео: {current_video}\n"
                                      f"Аудио: {current_audio}")

    video_markup = types.InlineKeyboardMarkup()
    for i, fmt in enumerate(VIDEO_FORMATS, 1):
        video_markup.add(types.InlineKeyboardButton(f"{i}. {fmt.upper()}", callback_data=f'video_{i}'))
    bot.send_message(message.chat.id, "Выбери формат для видео:", reply_markup=video_markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('video_'))
def handle_video_format(call):
    user_id = call.from_user.id
    choice = call.data.split('_')[1]
    if 1 <= int(choice) <= len(VIDEO_FORMATS):
        fmt = VIDEO_FORMATS[int(choice) - 1]
        update_user_setting(user_id, 'video_format', fmt)
        bot.answer_callback_query(call.id, f"Формат видео: {fmt}")
        audio_markup = types.InlineKeyboardMarkup()
        for i, fmt_audio in enumerate(AUDIO_FORMATS, 1):
            audio_markup.add(types.InlineKeyboardButton(f"{i}. {fmt_audio.upper()}", callback_data=f'audio_{i}'))
        bot.send_message(call.message.chat.id, "Теперь выбери формат для аудио:", reply_markup=audio_markup)
    else:
        bot.answer_callback_query(call.id, "Неверный выбор")


@bot.callback_query_handler(func=lambda call: call.data.startswith('audio_'))
def handle_audio_format(call):
    user_id = call.from_user.id
    choice = call.data.split('_')[1]
    if 1 <= int(choice) <= len(AUDIO_FORMATS):
        fmt = AUDIO_FORMATS[int(choice) - 1]
        update_user_setting(user_id, 'audio_format', fmt)
        bot.answer_callback_query(call.id, f"Формат аудио: {fmt}")
        bot.send_message(call.message.chat.id, "Форматы обновлены!")
    else:
        bot.answer_callback_query(call.id, "Неверный выбор")


@bot.message_handler(func=lambda m: m.text == "О программе")
def about(message):
    about_text = """
Об авторе:

Создано Drayn

Где я обитаю:

1. 𝕏 Twitter: https://twitter.com/thedrayndev

2. 🤖 Reddit: https://www.reddit.com/user/DraynHGames

3. ☎️ Discord: https://discord.gg/bPHuW7f7MJ

4. 💌 Telegram: https://t.me/drayns_campfire

Купить мне кофе:

⚡ Boosty: https://boosty.to/drayn

С любовью, Ваш Драник <3
"""
    bot.send_message(message.chat.id, about_text)


if __name__ == "__main__":
    user_settings = load_user_settings()
    bot.polling(none_stop=True)