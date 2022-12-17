from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from pytube import YouTube
import sqlite3
import config

connect = sqlite3.connect('users.db')
cur  = connect.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
    username VARCHAR(255),
    id INTEGER,
    chat_id INTEGER
    );
    """)
connect.commit()


bot = Bot(config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    cur  = connect.cursor()
    cur.execute(f"SELECT id FROM users WHERE  id  == {message.from_user.id};")
    result = cur.fetchall()
    if result ==[]:
        cur.execute(f"INSERT INTO users VALUES ('{message.from_user.username}', {message.from_user.id}, {message.chat.id});")
    connect.commit()
    await message.answer(f'Здравствуйте, я помогу показать информацию о видео в Ютубе, а также могу рассылать сообщения')

class MailingState(StatesGroup):
    mailing = State()


@dp.message_handler(commands=["mailing"])
async def mailing(message : types.Message):
    await message.answer('Что нужно рассылать: ')
    await MailingState.mailing.set()
    


@dp.message_handler(state=MailingState.mailing)
async def mailing(message : types.Message, state : FSMContext):

    try:
        await message.answer("Началась рассылка")
        
        cur.execute("SELECT chat_id FROM users;")
        result = cur.fetchall()
        for i in result:

            await bot.send_message(chat_id=int(i[0]), text = message.text)
        await state.finish()
    except:
        await message.answer("Произошла ошибка, повторите попытку позже")
        await state.finish()

class InfoVideo(StatesGroup):
    info = State()


@dp.message_handler(commands=["video_info"])
async def info_video(message: types.Message):
    await message.answer("Отправьте ссылку на видео в ютубе и я дам вам о нем информацию")
    await InfoVideo.info.set()

@dp.message_handler(state=InfoVideo.info)
async def info_video(message: types.Message, state: FSMContext):
    res = message.text.split()
    video = YouTube(str(res))
    print(video.description)
    await message.reply(f"Автор: {video.author}.\n Просмотры: {video.views}.\n Дата выхода: {video.publish_date}.\nДлина видео: {video.length}сек.\n Описание:\n {video.description}.")
    await state.finish()


@dp.message_handler()
async def not_found(message: types.Message):
    await message.reply("Я вас не понял введите /help")

executor.start_polling(dp)
