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

# Import database and export functions
from db_manager import init_db, register_user, log_analysis, get_user_stats, get_leaderboard, get_full_history_df

# --- CONFIGURATION ---
TOKEN = "8727076479:AAGx6KbDVI2IEieEy1Su-PPsxW2nm9kBfOk"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# NLTK Downloads
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

logging.basicConfig(level=logging.INFO)

def process_text_analysis(text):
    """Analyzes text and creates a frequency chart."""
    blob = TextBlob(text)
    sentences_count = len(blob.sentences)
    sentiment = blob.sentiment.polarity 

    # Cleaning
    clean_text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    words = nltk.word_tokenize(clean_text)
    
    stop_words = set(stopwords.words('english')) | set(stopwords.words('russian'))
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]

    word_counts = Counter(filtered_words)
    common_words = word_counts.most_common(10)

    mood = "Neutral"
    if sentiment > 0.1: mood = "Positive 😊"
    elif sentiment < -0.1: mood = "Negative 😟"

    if common_words:
        words_list, counts = zip(*common_words)
        plt.figure(figsize=(10, 6))
        plt.bar(words_list, counts, color='skyblue', edgecolor='navy')
        plt.title('Top 10 Frequent Words')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('bot_chart.png')
        plt.close()

    return sentences_count, len(filtered_words), mood, sentiment

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 **Welcome to the Professional Text Analyzer!**\n\n"
        "Commands:\n"
        "🏆 /top - View leaderboard\n"
        "📊 /export - Download your analysis history in Excel\n\n"
        "Send me a **.txt file** or **text message** to analyze!"
    )

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    leaders = get_leaderboard()
    if not leaders:
        await message.answer("🏆 The leaderboard is empty.")
        return
    text = "🏆 **Top 5 Most Active Users:**\n\n"
    for i, (username, count) in enumerate(leaders, 1):
        name = f"@{username}" if username else "Anonymous"
        text += f"{i}. {name} — {count} analyses\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("export"))
async def cmd_export(message: types.Message):
    await message.answer("Generating your Excel report... ⏳")
    df = get_full_history_df(message.from_user.id)
    
    if df.empty:
        await message.answer("You have no history to export.")
        return

    file_name = f"report_{message.from_user.id}.xlsx"
    df.to_excel(file_name, index=False)
    
    document = FSInputFile(file_name)
    await message.answer_document(document, caption="Here is your full analysis history! 📈")
    os.remove(file_name) # Delete temporary file

@dp.message(F.document)
async def handle_document(message: types.Message):
    if not message.document.file_name.endswith('.txt'):
        await message.answer("❌ Please send .txt files only.")
        return

    register_user(message.from_user.id, message.from_user.username)
    user_total = get_user_stats(message.from_user.id)

    file_info = await bot.get_file(message.document.file_id)
    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{message.document.file_name}"
    await bot.download_file(file_info.file_path, file_path)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    s_count, w_count, mood, score = process_text_analysis(content)
    log_analysis(message.from_user.id, score)

    caption = (
        f"📊 **File Analysis: {message.document.file_name}**\n"
        f"---------------------------\n"
        f"[*] Sentences: {s_count}\n"
        f"[*] Sentiment: {mood} ({score:.2f})\n\n"
        f"👤 **Your Stats:**\n"
        f"Total analyses: {user_total}"
    )
    chart = FSInputFile("bot_chart.png")
    await message.answer_photo(chart, caption=caption, parse_mode="Markdown")

@dp.message(F.text & ~F.command)
async def handle_text_message(message: types.Message):
    if len(message.text) < 10:
        await message.answer("ℹ️ Please send at least 10 characters.")
        return

    register_user(message.from_user.id, message.from_user.username)
    user_total = get_user_stats(message.from_user.id)

    s_count, w_count, mood, score = process_text_analysis(message.text)
    log_analysis(message.from_user.id, score)

    caption = (
        f"📝 **Quick Text Report**\n"
        f"---------------------------\n"
        f"[*] Sentiment: {mood} ({score:.2f})\n\n"
        f"👤 **User Progress:**\n"
        f"This is your analysis #{user_total}!"
    )
    chart = FSInputFile("bot_chart.png")
    await message.answer_photo(chart, caption=caption, parse_mode="Markdown")

async def main():
    init_db()
    print("[OK] Bot and Database started.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")