import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import re

API_TOKEN = 'ВАШ-ТОКЕН'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

reminders = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "⏰ Привет! Я бот-будильник!\n\n"
        "📌 Команды:\n"
        "/set 10:30 Купить молоко — установить напоминание\n"
        "/list — показать мои напоминания\n"
        "/clear — удалить все напоминания\n"
        "/help — показать это сообщение"
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await cmd_start(message)

@dp.message(Command("set"))
async def set_reminder(message: types.Message):
    try:
        text = message.text.replace("/set", "").strip()
        
        parts = text.split(" ", 1)
        
        if len(parts) < 2:
            await message.answer(
                "❌ Неправильный формат!\n"
                "Используй: /set 10:30 Текст напоминания"
            )
            return
        
        time_str = parts[0]
        reminder_text = parts[1]
        
        if not re.match(r"^\d{1,2}:\d{2}$", time_str):
            await message.answer(
                "❌ Неверный формат времени!\n"
                "Используй ЧЧ:ММ (например, 10:30)"
            )
            return
        
        hours, minutes = map(int, time_str.split(":"))
        
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            await message.answer("❌ Время должно быть от 00:00 до 23:59")
            return
        
        now = datetime.now()
        alarm_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        
        if alarm_time <= now:
            alarm_time += timedelta(days=1)
        
        user_id = message.from_user.id
        reminders[user_id] = (alarm_time, reminder_text)
        
        await message.answer(
            f"✅ Напоминание установлено!\n\n"
            f"⏰ Время: {alarm_time.strftime('%H:%M')}\n"
            f"📝 Текст: {reminder_text}\n\n"
            f"🔄 Бот пришлёт уведомление в указанное время."
        )
        
        asyncio.create_task(check_reminder(user_id, alarm_time, reminder_text))
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}\nПопробуй ещё раз.")

@dp.message(Command("list"))
async def list_reminders(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in reminders:
        await message.answer("📭 У тебя нет активных напоминаний.")
        return
    
    alarm_time, text = reminders[user_id]
    await message.answer(
        f"📋 Твоё напоминание:\n\n"
        f"⏰ {alarm_time.strftime('%H:%M')}\n"
        f"📝 {text}"
    )

@dp.message(Command("clear"))
async def clear_reminders(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in reminders:
        del reminders[user_id]
        await message.answer("🗑 Все напоминания удалены!")
    else:
        await message.answer("📭 У тебя нет активных напоминаний.")

async def check_reminder(user_id, alarm_time, text):
    """Фоновая задача: проверяет время и отправляет уведомление"""
    while True:
        now = datetime.now()
        if now >= alarm_time:
            await bot.send_message(
                user_id,
                f"🔔 НАПОМИНАНИЕ!\n\n"
                f"📝 {text}\n"
                f"⏰ Время: {alarm_time.strftime('%H:%M')}"
            )
            if user_id in reminders:
                del reminders[user_id]
            break
        await asyncio.sleep(30)

@dp.message()
async def echo(message: types.Message):
    """Если пользователь просто пишет текст (без команд) — отвечаем эхом"""
    await message.answer(f"Ты написал: {message.text}")

async def main():
    print("⏰ Бот-будильник запущен!")
    print("Жду сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())