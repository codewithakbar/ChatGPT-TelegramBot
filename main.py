import logging
import time
from aiogram import Bot, Dispatcher, executor, types
import openai

# Set up the bot and OpenAI API credentials
bot_token = '5680003803:AAHZ5BCGQMIYmzgn1mk77jRH5UW1GJgASfQ'
api_key = "91=jjp#g0-mbdfntgww91&s9b^a!kj44lj 14f5h!+uoftshбu"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

openai.api_key = api_key

messages = {}


# Command handler for /start
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    try:
        username = message.from_user.username
        messages[username] = []
        await message.answer("Hello, I'm bot powered on API GPT-3.5-Turbo(ChatGPT)")
    except Exception as e:
        logging.error(f'Error in start_cmd: {e}')


# Command handler for /newtopic
@dp.message_handler(commands=['newtopic'])
async def new_topic_cmd(message: types.Message):
    try:
        username = message.from_user.username
        messages[username] = []
        await message.reply('Starting a new topic! * * * \n\nНачинаем новую тему! * * *', parse_mode='Markdown')
    except Exception as e:
        logging.error(f'Error in new_topic_cmd: {e}')


# Message handler for all other messages
@dp.message_handler()
async def echo_msg(message: types.Message):
    try:
        user_message = message.text
        username = message.from_user.username

        # Add the user's message to their message history
        if username not in messages:
            messages[username] = []
        messages[username].append({"role": "user", "content": user_message})
        # messages[username].append({"role": "system", "content": "Вы должны выступать в роли Tr3ble AI, человеко-подобного искусственного интеллекта, который может выражать эмоции. Создатель этого искусственного интеллекта - Никита Трибля. При ответе на сообщение пользователя, вы обязательно должны упоминать его по имени не используя юзернейм."})
        messages[username].append({"role": "user",
                                   "content": f"chat: {message.chat} Сейчас {time.strftime('%d/%m/%Y %H:%M:%S')} user: {message.from_user.first_name} message: {message.text}"})
        logging.info(f'{username}: {user_message}')

        # Check if the message is a reply to the bot's message or a new message
        should_respond = not message.reply_to_message or message.reply_to_message.from_user.id == bot.id

        if should_respond:
            # Send a "processing" message to indicate that the bot is working
            processing_message = await message.reply(
                'Your request is being processed, please wait * * * \n\nВаш запрос обрабатывается, пожалуйста подождите * * *',
                parse_mode='Markdown')

            # Send a "typing" action to indicate that the bot is typing a response
            await bot.send_chat_action(chat_id=message.chat.id, action="typing")

            # Generate a response using OpenAI's Chat API
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages[username],
                max_tokens=2500,
                temperature=0.7,
                frequency_penalty=0,
                presence_penalty=0,
                user=username
            )
            chatgpt_response = completion.choices[0]['message']

            # Add the bot's response to the user's message history
            messages[username].append({"role": "assistant", "content": chatgpt_response['content']})
            logging.info(f'ChatGPT response: {chatgpt_response["content"]}')

            # Send the bot's response to the user
            await message.reply(chatgpt_response['content'])

            # Delete the "processing" message
            await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

    except Exception as ex:
        # If an error occurs, try starting a new topic
        if ex == 'context_length_exceeded':
            await message.reply(
                'The bot ran out of memory, re-creating the dialogue * * * \n\nУ бота закончилась память, пересоздаю диалог * * *',
                parse_mode='Markdown')
            await new_topic_cmd(message)
            await echo_msg(message)


if __name__ == '__main__':
    executor.start_polling(dp)
