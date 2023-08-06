"""Provide a simple greeting handler for a Le bot."""


from telegram.ext import CommandHandler as _CommandHandler


def _hello(bot, update):
    """Greet the user using own name."""
    message = "Hi all, I'm {bot.first_name}.".format(bot=bot)
    bot.send_message(update.message.chat_id, message)


_handler = _CommandHandler('hi', _hello)
