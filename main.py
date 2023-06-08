import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor

import db

API_TOKEN = "YOUR_TOKEN_FROM_BOTFATHER"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

ADMIN_IDS = []  # paste your id from your tg profile
MODERATOR_IDS = []  #  paste your id from your tg profile (or your friends :)) 

BOT_ACTIVE = False

def is_admin_or_moderator(user_id):
    return user_id in ADMIN_IDS or user_id in MODERATOR_IDS

def is_bot_active():
    return BOT_ACTIVE

@dp.message_handler(content_types=["new_chat_members"])
async def on_new_chat_member(message: types.Message):
    if is_bot_active():
        for new_member in message.new_chat_members:
            await message.reply(f"Привет, {new_member.full_name}! Добро пожаловать в чат!")

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    global BOT_ACTIVE

    chat_id = message.chat.id
    if is_admin_or_moderator(message.from_user.id):
        BOT_ACTIVE = True
        await bot.send_message(chat_id, "Бот активирован и готов к работе!")
    else:
        await message.reply("У вас нет прав для использования этой команды.")

@dp.message_handler(commands=["stop"])
async def cmd_stop(message: types.Message):
    global BOT_ACTIVE

    chat_id = message.chat.id
    if is_admin_or_moderator(message.from_user.id):
        BOT_ACTIVE = False
        await bot.send_message(chat_id, "Бот деактивирован. Для активации используйте /start.")
    else:
        await message.reply("У вас нет прав для использования этой команды.")

@dp.message_handler(commands=["ban"])
async def cmd_ban(message: types.Message):
    if not is_bot_active():
        await message.reply("Бот остановлен. Обратитесь к администратору.")
        return
    if is_admin_or_moderator(message.from_user.id):
        user_to_ban = message.reply_to_message.from_user
        if user_to_ban:
            chat_id = message.chat.id
            user_id = user_to_ban.id

            if not db.is_user_banned(chat_id, user_id):
                db.ban_user(chat_id, user_id)
                db.clear_warnings(chat_id, user_id)

                await bot.kick_chat_member(chat_id=chat_id, user_id=user_id)
                await message.reply(f"Пользователь {user_to_ban.full_name} забанен.")
            else:
                await message.reply("Пользователь уже забанен.")
        else:
            await message.reply("Пожалуйста, используйте эту команду в ответ на сообщение пользователя, которого хотите забанить.")
    else:
        await message.reply("У вас нет прав для использования этой команды.")

@dp.message_handler(commands=["mute"])
async def cmd_mute(message: types.Message):
    if not is_bot_active():
        await message.reply("Бот остановлен. Обратитесь к администратору.")
        return
    if is_admin_or_moderator(message.from_user.id):
        user_to_mute = message.reply_to_message.from_user
        if user_to_mute:
            chat_id = message.chat.id
            user_id = user_to_mute.id

            if not db.is_user_muted(chat_id, user_id):
                db.mute_user(chat_id, user_id)
                db.clear_warnings(chat_id, user_id)

                # Изменить настройки разрешений для замученного пользователя
                mute_permissions = types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )

                await bot.restrict_chat_member(chat_id=message.chat.id, user_id=user_to_mute.id, permissions=mute_permissions)
                await message.reply(f"Пользователь {user_to_mute.full_name} замучен.")
            else:
                await message.reply("Пользователь уже замучен.")
        else:
            await message.reply("Пожалуйста, используйте эту команду в ответ на сообщение пользователя, которого хотите замутить.")
    else:
        await message.reply("У вас нет прав для использования этой команды.")

async def send_unban_notification(user_id, invite_link):
    try:
        await bot.send_message(user_id, f"Вы были разбанены. Теперь вы можете вернуться в группу, пройдя по этой ссылке: {invite_link}")
    except Exception as e:
        logging.exception(f"Не удалось отправить уведомление о разбане пользователю {user_id}. Ошибка: {e}")

@dp.message_handler(commands=["unban"])
async def cmd_unban(message: types.Message):
    if not is_bot_active():
        await message.reply("Бот остановлен. Обратитесь к администратору.")
        return
    if is_admin_or_moderator(message.from_user.id):
        user_to_unban = message.reply_to_message.from_user
        if user_to_unban:
            chat_id = message.chat.id
            user_id = user_to_unban.id

            if db.is_user_banned(chat_id, user_id):
                db.unban_user(chat_id, user_id)

                await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
                await message.reply(f"Пользователь {user_to_unban.full_name} разбанен.")
                await send_unban_notification(user_id, "https://t.me/+o3iBUjY1vfJkOTgy")
            else:
                await message.reply("Пользователь не забанен.")
        else:
            await message.reply("Пожалуйста, используйте эту команду в ответ на сообщение пользователя, которого хотите разбанить.")
    else:
        await message.reply("У вас нет прав для использования этой команды.")


@dp.message_handler(commands=["unmute"])
async def cmd_unmute(message: types.Message):
    if not is_bot_active():
        await message.reply("Бот остановлен. Обратитесь к администратору.")
        return

    if is_admin_or_moderator(message.from_user.id):
        user_to_unmute = message.reply_to_message.from_user
        if user_to_unmute:
            chat_id = message.chat.id
            user_id = user_to_unmute.id

            if db.is_user_muted(chat_id, user_id):
                db.unmute_user(chat_id, user_id)

                un_mute_permissions = types.ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )

                await bot.restrict_chat_member(chat_id=message.chat.id, user_id=user_to_unmute.id, permissions=un_mute_permissions)
                await message.reply(f"Пользователь {user_to_unmute.full_name} размучен.")
            else:
                await message.reply("Пользователь не замучен.")
        else:
            await message.reply("Пожалуйста, используйте эту команду в ответ на сообщение пользователя, которого хотите размутить.")
    else:
        await message.reply("У вас нет прав для использования этой команды.")


@dp.message_handler(commands=["warn"])
async def cmd_warn(message: types.Message):
    if not is_bot_active():
        await message.reply("Бот остановлен. Обратитесь к администратору.")
        return
    if is_admin_or_moderator(message.from_user.id):
        user_to_warn = message.reply_to_message.from_user
        if user_to_warn:
            chat_id = message.chat.id
            user_id = user_to_warn.id

            db.add_warning(chat_id, user_id)
            warnings_count = db.get_warnings(chat_id, user_id) # Используем функцию get_warnings вместо get_warnings_count

            if warnings_count >= 2:
                # Мутим пользователя, как и в команде mute
                mute_permissions = types.ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )

                await bot.restrict_chat_member(chat_id=message.chat.id, user_id=user_to_warn.id, permissions=mute_permissions)
                await message.reply(f"Пользователь {user_to_warn.full_name} замучен после 2 предупреждений.")
            else:
                await message.reply(f"Пользователь {user_to_warn.full_name} получил предупреждение. Всего предупреждений: {warnings_count}.")
        else:
            await message.reply("Пожалуйста, используйте эту команду в ответ на сообщение пользователя, которому хотите выдать предупреждение.")
    else:
        await message.reply("У вас нет прав для использования этой команды.")

@dp.message_handler(commands=["clear_warnings"])
async def cmd_clear_warnings(message: types.Message):
    if not is_bot_active():
        await message.reply("Бот остановлен. Обратитесь к администратору.")
        return
    if is_admin_or_moderator(message.from_user.id):
        if message.reply_to_message:
            user_to_clear_warnings = message.reply_to_message.from_user
            if user_to_clear_warnings:
                chat_id = message.chat.id
                user_id = user_to_clear_warnings.id

                db.clear_warnings(chat_id, user_id)

                if db.is_user_muted(chat_id, user_id):
                    db.unmute_user(chat_id, user_id)

                un_mute_permissions = types.ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )

                await bot.restrict_chat_member(chat_id=message.chat.id, user_id=user_to_clear_warnings.id, permissions=un_mute_permissions)
                await message.reply(f"Предупреждения для пользователя {user_to_clear_warnings.full_name} сброшены и пользователь размучен.")
            else:
                await message.reply("Пожалуйста, используйте эту команду в ответ на сообщение пользователя, для которого хотите сбросить предупреждения.")
        else:
            await message.reply("Пожалуйста, используйте эту команду в ответ на сообщение пользователя, для которого хотите сбросить предупреждения.")
    else:
        await message.reply("У вас нет прав для использования этой команды.")



if __name__ == "__main__":
    from aiogram import executor

    db.init()
    executor.start_polling(dp, skip_updates=True)
