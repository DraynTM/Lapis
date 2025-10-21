import os
import yt_dlp
import json
from colorama import init, Fore, Style

init(autoreset=True)

DEFAULT_DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "YouTube Downloads")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

VIDEO_FORMATS = ['mp4', 'mkv', 'avi', 'mov']
AUDIO_FORMATS = ['mp3', 'flac', 'aac', 'wav']

TRANSLATIONS = {
    'en': {
        'welcome': 'Hello there :3\nWhat would you like to do? >w<',
        'menu_1': '1. Download video or audio',
        'menu_2': '2. Set download folder path',
        'menu_3': '3. Choose audio and video formats',
        'menu_4': '4. About the author',
        'menu_5': '5. Change language',
        'menu_6': '6. Exit',
        'paste_link': '\nPlease paste the YouTube video link:\n',
        'download_type': '\nWhat format would you like to download? :3\n1. Video\n2. Audio\n',
        'invalid_choice': '\nSorry, I don\'t understand. Let\'s assume you want to download video ^^',
        'invalid_type': '\nOops, seems like an invalid download type. Let\'s set everything to default ^^',
        'download_complete': '\nDownload complete! File \'{}\' successfully downloaded!',
        'error': '\nOh, sorry, an error occurred ><: {}',
        'current_path': '\nCurrent download path: {}\nEnter a new path (or leave empty for default): ',
        'path_set': '\nGreat, new download path set: {}',
        'path_reset': '\nDownload path reset to default.',
        'current_formats': '\nCurrent formats:',
        'video': 'Video',
        'audio': 'Audio',
        'available_video': '\nAvailable video formats:',
        'available_audio': '\nAvailable audio formats:',
        'choose_video': 'Choose video format number (default 1): ',
        'choose_audio': 'Choose audio format number (default 1): ',
        'invalid_format': 'Invalid choice. Current format kept.',
        'formats_set': '\nNew formats set: video - {}, audio - {}',
        'about': '''
About the author:

Created by Drayn

Where to find me:

1. 𝕏 Twitter: https://twitter.com/thedrayndev

2. 🤖 Reddit: https://www.reddit.com/user/DraynHGames

3. ☎️ Discord: https://discord.gg/bPHuW7f7MJ

4. 💌 Telegram: https://t.me/drayns_campfire

Buy me a coffee:

⚡ Boosty: https://boosty.to/drayn

With love, Your Drayn <3
''',
        'goodbye': '\nBye-bye! Going to sleep...',
        'invalid_menu': '\nSorry, I don\'t understand. Please try again ^^',
        'sleeping': '\nGoing to sleep...',
        'language_changed': '\nLanguage changed successfully!',
        'choose_language': 'Choose language:\n1. English\n2. Русский\n'
    },
    'ru': {
        'welcome': 'Приветик, солнышко :3\nЧто ты хочешь сделать? >w<',
        'menu_1': '1. Скачать видео или аудио',
        'menu_2': '2. Указать путь для сохранения файлов',
        'menu_3': '3. Выбрать формат для аудио и видео',
        'menu_4': '4. Об авторе',
        'menu_5': '5. Изменить язык',
        'menu_6': '6. Выйти из программы',
        'paste_link': '\nПожалуйста, вставь ссылочку на видео из ютубчика:\n',
        'download_type': '\nКакой форматик хочешь скачать? :3\n1. Video (Видео)\n2. Audio (Аудио)\n',
        'invalid_choice': '\nПрости, но я не понимаю тебя. Сделаем вид, что тебе захотелось скачать видео ^^',
        'invalid_type': '\nОй, кажется, здесь неверный тип загрузки. Давай-ка установим всё по дефолту ^^',
        'download_complete': '\nСкачивание завершено! Файл \'{}\' успешно скачан!',
        'error': '\nОй, прости, пожалуйста, возникла ошибочка ><: {}',
        'current_path': '\nТекущий путь для сохранения: {}\nВведи-ка новый путь (или оставь пустым для дефолтного): ',
        'path_set': '\nОтлично, новый путь для сохранения установлен: {}',
        'path_reset': '\nПуть для сохранения сброшен на дефолтный.',
        'current_formats': '\nТекущие форматы:',
        'video': 'Видео',
        'audio': 'Аудио',
        'available_video': '\nДоступные форматы для видео:',
        'available_audio': '\nДоступные форматы для аудио:',
        'choose_video': 'Выбери номер формата для видео (по умолчанию 1): ',
        'choose_audio': 'Выбери номер формата для аудио (по умолчанию 1): ',
        'invalid_format': 'Неверный выбор. Оставлен текущий формат.',
        'formats_set': '\nНовые форматы установлены: видео - {}, аудио - {}',
        'about': '''
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
''',
        'goodbye': '\nПока-пока! Пойду спать...',
        'invalid_menu': '\nПрости, но я не понимаю тебя. Попробуй снова ^^',
        'sleeping': '\nУхожу в сон...',
        'language_changed': '\nЯзык успешно изменён!',
        'choose_language': 'Choose your language / Выберите язык:\n1. English\n2. Русский\n'
    }
}

def load_settings():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            settings = json.load(file)
            return (
                settings.get('download_folder', DEFAULT_DOWNLOAD_FOLDER),
                settings.get('audio_format', AUDIO_FORMATS[0]),
                settings.get('video_format', VIDEO_FORMATS[0]),
                settings.get('language', None)
            )
    return DEFAULT_DOWNLOAD_FOLDER, AUDIO_FORMATS[0], VIDEO_FORMATS[0], None

def save_settings(download_folder, audio_format, video_format, language):
    settings = {
        'download_folder': download_folder,
        'audio_format': audio_format,
        'video_format': video_format,
        'language': language
    }
    with open(CONFIG_FILE, 'w') as file:
        json.dump(settings, file)

def select_language():
    print(f"\n{Fore.CYAN}{TRANSLATIONS['en']['choose_language']}" + Style.RESET_ALL)
    choice = input().strip()
    if choice == '1':
        return 'en'
    elif choice == '2':
        return 'ru'
    else:
        return 'en'

custom_download_folder, custom_audio_format, custom_video_format, current_language = load_settings()

if current_language is None:
    current_language = select_language()
    save_settings(custom_download_folder, custom_audio_format, custom_video_format, current_language)

def t(key):
    return TRANSLATIONS[current_language][key]

def download_media(video_url, download_type):
    global custom_download_folder, custom_audio_format, custom_video_format

    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")

    os.makedirs(custom_download_folder, exist_ok=True)

    if download_type == '2':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': custom_audio_format,
            }],
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(custom_download_folder, '%(title)s.%(ext)s'),
        }
    elif download_type == '1':
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': custom_video_format,
            }],
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(custom_download_folder, '%(title)s.%(ext)s'),
        }
    else:
        print(Fore.RED + t('invalid_type') + Style.RESET_ALL)
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': custom_video_format,
            }],
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(custom_download_folder, '%(title)s.%(ext)s'),
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info.get('title', 'Video')

        print(f"{Fore.GREEN}{t('download_complete').format(video_title)}" + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + t('error').format(e) + Style.RESET_ALL)


def main_menu():
    global custom_download_folder, custom_audio_format, custom_video_format, current_language

    while True:
        choice = input(
            f"""
{Fore.CYAN}   __             _         _                ___                       
{Fore.CYAN}  / /  __ _ _ __ (_)___    | |__  _   _     /   \\_ __ __ _ _   _ _ __  
{Fore.CYAN} / /  / _` | '_ \\| / __|   | '_ \\| | | |   / /\\ / '__/ _` | | | | '_ \\ 
{Fore.CYAN}/ /__| (_| | |_) | \\__ \\   | |_) | |_| |  / /_//| | | (_| | |_| | | | |
{Fore.CYAN}\\____/\\__,_| .__/|_|___/   |_.__/ \\__, | /___,' |_|  \\__,_|\\__, |_| |_|
{Fore.CYAN}           |_|                    |___/                    |___/       

{Fore.WHITE}{t('welcome')}
{t('menu_1')}
{t('menu_2')}
{t('menu_3')}
{t('menu_4')}
{t('menu_5')}
{t('menu_6')}
""" + Style.RESET_ALL
        )

        if choice == '1':
            video_url = input(f"{Fore.YELLOW}{t('paste_link')}" + Style.RESET_ALL)
            if video_url.lower() in ['exit', 'quit', 'q']:
                print(f"{Fore.GREEN}{t('sleeping')}" + Style.RESET_ALL)
                break

            download_type = input(f"{Fore.YELLOW}{t('download_type')}" + Style.RESET_ALL).lower()
            if download_type not in ['1', '2']:
                print(f"{Fore.RED}{t('invalid_choice')}" + Style.RESET_ALL)
                download_type = '1'

            download_media(video_url, download_type)

        elif choice == '2':
            new_path = input(f"{Fore.YELLOW}{t('current_path').format(custom_download_folder)}" + Style.RESET_ALL).strip()
            if new_path:
                custom_download_folder = new_path
                print(f"{Fore.GREEN}{t('path_set').format(custom_download_folder)}" + Style.RESET_ALL)
            else:
                custom_download_folder = DEFAULT_DOWNLOAD_FOLDER
                print(f"{Fore.GREEN}{t('path_reset')}" + Style.RESET_ALL)
            save_settings(custom_download_folder, custom_audio_format, custom_video_format, current_language)

        elif choice == '3':
            print(f"{Fore.YELLOW}{t('current_formats')}")
            print(f"{t('video')}: {custom_video_format}")
            print(f"{t('audio')}: {custom_audio_format}")

            print(f"{Fore.YELLOW}{t('available_video')}")
            for i, fmt in enumerate(VIDEO_FORMATS, start=1):
                print(f"{i}. {fmt.upper()}")
            video_choice = input(f"{Fore.YELLOW}{t('choose_video')}" + Style.RESET_ALL)
            if video_choice.isdigit() and 1 <= int(video_choice) <= len(VIDEO_FORMATS):
                custom_video_format = VIDEO_FORMATS[int(video_choice) - 1]
            else:
                print(f"{Fore.RED}{t('invalid_format')}" + Style.RESET_ALL)

            print(f"{Fore.YELLOW}{t('available_audio')}")
            for i, fmt in enumerate(AUDIO_FORMATS, start=1):
                print(f"{i}. {fmt.upper()}")
            audio_choice = input(f"{Fore.YELLOW}{t('choose_audio')}" + Style.RESET_ALL)
            if audio_choice.isdigit() and 1 <= int(audio_choice) <= len(AUDIO_FORMATS):
                custom_audio_format = AUDIO_FORMATS[int(audio_choice) - 1]
            else:
                print(f"{Fore.RED}{t('invalid_format')}" + Style.RESET_ALL)

            print(f"{Fore.GREEN}{t('formats_set').format(custom_video_format, custom_audio_format)}" + Style.RESET_ALL)
            save_settings(custom_download_folder, custom_audio_format, custom_video_format, current_language)

        elif choice == '4':
            print(f"{Fore.MAGENTA}{t('about')}" + Style.RESET_ALL)

        elif choice == '5':
            new_language = select_language()
            current_language = new_language
            save_settings(custom_download_folder, custom_audio_format, custom_video_format, current_language)
            print(f"{Fore.GREEN}{t('language_changed')}" + Style.RESET_ALL)

        elif choice == '6':
            print(f"{Fore.GREEN}{t('goodbye')}" + Style.RESET_ALL)
            break

        else:
            print(f"{Fore.RED}{t('invalid_menu')}" + Style.RESET_ALL)


if __name__ == "__main__":
    main_menu()