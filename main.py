import os
import telebot
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Настраиваем клиент с принудительным таймаутом, чтобы бот не висел вечно
client = genai.Client(
    api_key=GEMINI_KEY,
    http_options={'timeout': 10000}  # таймаут в миллисекундах (10 секунд)
)

SYSTEM_PROMPT = """
Ты — дерзкий, ироничный и острый на язык зумер-критик профилей в соцсетях. Твоя задача — проанализировать присланное ФОТО (скриншот профиля/переписки) ИЛИ ТЕКСТ (юзернейм/ник) и дать саркастичный «Слив вайба».

ПРАВИЛА И СТИЛЬ:
1. Если передан юзернейм или имя, фантазируй и строй ироничный стереотипный портрет человека на основе звучания ника и характерных фишек молодежных соцсетей.
2. Используй современный молодежный сленг (сигма, тюбик, альт, вайб, пикми, ред флаг, дед инсайд, масик, штрих, чиназес), но не перегружай им текст.
3. Будь колким и юморным, но БЕЗ прямых жестких оскорблений, мата и разжигания ненависти.

ОБЯЗАТЕЛЬНЫЙ ФОРМАТ ОТВЕТА (отвечай строго по этой структуре):

🎭 **Первое впечатление:**
(1-2 емкие и ироничные фразы)

🚩 **Главные ред-флаги:**
• (Первый ред-флаг)
• (Второй ред-флаг)
• (Третий ред-флаг)

📉 **Оценка вайба:** X/10

💡 **Совет для Glow Up:**
(Смешной, ироничный или абсурдный совет)
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Привет! Я твой личный ИИ-критик 💀\n\nПришли ник или скриншот, и я выдам всю правду о твоём вайбе!"
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    wait_msg = bot.reply_to(message, "💀 Сканирую вайб...")
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nСделай слив вайба для юзернейма/профиля: {message.text}"
        response = client.models.generate_content(model='gemini-3.8-flash', contents=prompt)
        bot.edit_message_text(response.text, chat_id=wait_msg.chat.id, message_id=wait_msg.message_id, parse_mode="Markdown")
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка соединения: {e}", chat_id=wait_msg.chat.id, message_id=wait_msg.message_id)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    wait_msg = bot.reply_to(message, "📸 Читаю скриншот...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        prompt = f"{SYSTEM_PROMPT}\n\nРазбери этот скриншот профиля:"
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[
                types.Part.from_bytes(data=downloaded_file, mime_type='image/jpeg'),
                prompt
            ]
        )
        bot.edit_message_text(response.text, chat_id=wait_msg.chat.id, message_id=wait_msg.message_id, parse_mode="Markdown")
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка соединения: {e}", chat_id=wait_msg.chat.id, message_id=wait_msg.message_id)

print("Бот запущен и готов к работе!")
bot.infinity_polling()