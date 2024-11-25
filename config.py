DISCORD_TOKEN = "420tokentokentokentoken.token.tokentokentokentokentoken" # Токен дискорд аккаунта
TELEGRAM_BOT_TOKEN = "7965745832:AAHDi4-p8udr43kMHarW6WwTtfMFPxJiN8o" # Токен телеграм бота, брать у @botfather
TELEGRAM_USER_IDs = [7538546817] # ID пользователей, которым будут присылаться уведомления (в начале пропиши /start боту)
messages_to_search = [ # Сообщения для поиска
    {
        'guild_id': 759270446478000179,
        'channel_id': 1280237431588782131,
        'text_to_search': 'сюда123',
        'search_parameters': {
            'is_lower': True,
            'is_equal': False
        }
    }
]
# search_parameters:
#   is_lower = перевод строки в нижний регистр
#   is_equal = точное сравнение