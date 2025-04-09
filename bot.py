import os
import telegram
from telegram.ext import Application, MessageHandler, filters
import openai
from dotenv import load_dotenv
import logging

load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
# Set higher logging level for httpx to avoid logging sensitive info from requests
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext.ExtBot").setLevel(logging.WARNING) # Also for the bot's internal http client



TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_BASEURL = os.getenv("OPENAI_BASEURL")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")
SYSTEM_MSG = os.getenv("SYSTEM_MSG")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Default model

if not all([TELEGRAM_BOT_TOKEN, OPENAI_BASEURL, OPENAI_TOKEN, SYSTEM_MSG]):
    logger.error("Missing environment variables. Please set TELEGRAM_BOT_TOKEN, OPENAI_BASEURL, OPENAI_TOKEN, and SYSTEM_MSG.")
    exit(1)


async def echo(update, context):
    bot = await context.bot.get_me()
    bot_name = bot.first_name
    bot_username = bot.username

    logger.info(f"Bot started with name: {bot_name} (@{bot_username})")

    if update.message and update.message.text:
        message_text = update.message.text
        first_sentence = message_text.split(".")[0] + "."  # Get the first sentence
        logger.info(f"Received message: {first_sentence}")
    else:
        await update.message.reply_text("i don't see text")
        return

    if bot_name in message_text or f"@{bot_username}" in message_text:
        try:
            client = openai.OpenAI(
                base_url=OPENAI_BASEURL,
                api_key=OPENAI_TOKEN
            )

            logger.info(f"Querying OpenAI API with model: {OPENAI_MODEL}")
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_MSG},
                    {"role": "user", "content": message_text}
                ],
                model=OPENAI_MODEL
            )

            response_text = chat_completion.choices[0].message.content
            first_response_sentence = response_text.split(".")[0] + "." if response_text else "No response text."
            logger.info(f"OpenAI API response: {first_response_sentence}")
            await update.message.reply_text(response_text, reply_to_message_id=update.message.message_id)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            await update.message.reply_text(f"An error occurred: {e}")
    else:
        # Ignore messages that don't mention the bot
        pass


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == '__main__':
    main()