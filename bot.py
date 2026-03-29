import os
import asyncio
import logging
import string
from collections import Counter

import nltk
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from textblob import TextBlob
from nltk.corpus import stopwords

from db_manager import init_db, register_user, log_analysis, get_user_stats, get_leaderboard

# --- CONFIGURATION ---
TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# NLTK Setup
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

logging.basicConfig(level=logging.INFO)

def process_text_analysis(text):
    """Core logic: analyzes text and creates a visual chart."""
    blob = TextBlob(text)
    sentences_count = len(blob.sentences)
    sentiment = blob.sentiment.polarity 

    # Text cleaning
    clean_text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    words = nltk.word_tokenize(clean_text)
    
    stop_words = set(stopwords.words('english')) | set(stopwords.words('russian'))
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]

    word_counts = Counter(filtered_words)
    common_words = word_counts.most_common(10)

    # Sentiment Mapping
    mood = "Neutral"
    if sentiment > 0.1: mood = "Positive 😊"
    elif sentiment < -0.1: mood = "Negative 😟"

    # Chart creation
    if common_words:
        words_list, counts = zip(*common_words)
        plt.figure(figsize=(10, 6))
        plt.bar(words_list, counts, color='skyblue', edgecolor='navy')
        plt.title('Top 10 Most Frequent Words')
        plt.xlabel('Words')
        plt.ylabel('Count')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('bot_chart.png')
        plt.close()

    return sentences_count, len(filtered_words), mood, sentiment

# --- COMMAND HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 **Welcome to the AI Text Analyzer!**\n\n"
        "I can help you analyze text sentiment and word frequency.\n"
        "🏆 Use /top to see the leaderboard.\n"
        "📝 Send me a **.txt file** or simply **type a message** to start!"
    )

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    """Shows the top 5 most active users."""
    leaders = get_leaderboard()
    if not leaders:
        await message.answer("🏆 The leaderboard is currently empty.")
        return

    text = "🏆 **Top 5 Text Analyzers:**\n\n"
    for i, (username, count) in enumerate(leaders, 1):
        name = f"@{username}" if username else "Anonymous"
        text += f"{i}. {name} — {count} analyses\n"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.document)
async def handle_document(message: types.Message):
    """Handles .txt file processing."""
    if not message.document.file_name.endswith('.txt'):
        await message.answer("❌ Error: I only accept **.txt** files.")
        return

    register_user(message.from_user.id, message.from_user.username)
    user_total = get_user_stats(message.from_user.id)

    file_info = await bot.get_file(message.document.file_id)
    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{message.document.file_name}"
    await bot.download_file(file_info.file_path, file_path)

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        s_count, w_count, mood, score = process_text_analysis(content)
        log_analysis(message.from_user.id, score)

        caption = (
            f"📊 **File Report: {message.document.file_name}**\n"
            f"---------------------------\n"
            f"[*] Sentences: {s_count}\n"
            f"[*] Sentiment: {mood} ({score:.2f})\n\n"
            f"👤 **Your Profile:**\n"
            f"Total requests: {user_total}"
        )

        chart = FSInputFile("bot_chart.png")
        await message.answer_photo(chart, caption=caption, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"⚙️ An error occurred: {e}")

@dp.message(F.text & ~F.command)
async def handle_text_message(message: types.Message):
    """Handles plain text messages."""
    if len(message.text) < 10:
        await message.answer("ℹ️ Text is too short for a meaningful analysis.")
        return

    register_user(message.from_user.id, message.from_user.username)
    user_total = get_user_stats(message.from_user.id)

    s_count, w_count, mood, score = process_text_analysis(message.text)
    log_analysis(message.from_user.id, score)

    caption = (
        f"📝 **Quick Analysis Report**\n"
        f"---------------------------\n"
        f"[*] Sentiment: {mood} ({score:.2f})\n\n"
        f"👤 **User Stats:**\n"
        f"This is your request #{user_total}!"
    )

    chart = FSInputFile("bot_chart.png")
    await message.answer_photo(chart, caption=caption, parse_mode="Markdown")

# --- RUN BOT ---

async def main():
    init_db() 
    print("[OK] Database is ready.")
    print("[OK] Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")