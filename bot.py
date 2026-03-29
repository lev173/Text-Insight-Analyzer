import os
import asyncio
import logging
import string
from collections import Counter

import nltk
import pandas as pd
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from textblob import TextBlob
from nltk.corpus import stopwords

# --- CONFIGURATION ---
# Replace with your actual token from @BotFather
TOKEN = "YOUR_BOT_TOKEN_HERE"

# Initialize Bot and Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# NLTK Downloads (Ensuring all resources are present)
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

# Setup logging
logging.basicConfig(level=logging.INFO)

def process_text_analysis(text):
    """
    Core logic: Analyzes text and generates a frequency chart.
    Returns: sentence count, word count, mood string, and sentiment score.
    """
    # 1. NLP Analysis
    blob = TextBlob(text)
    sentences_count = len(blob.sentences)
    sentiment = blob.sentiment.polarity 

    # 2. Text Cleaning
    clean_text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    words = nltk.word_tokenize(clean_text)
    
    # Filtering stop words (English & Russian)
    stop_words = set(stopwords.words('english')) | set(stopwords.words('russian'))
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]

    # 3. Stats & Chart
    word_counts = Counter(filtered_words)
    common_words = word_counts.most_common(10)

    mood = "Neutral"
    if sentiment > 0.1: mood = "Positive 😊"
    elif sentiment < -0.1: mood = "Negative 😟"

    # Create and save chart
    if common_words:
        words_list, counts = zip(*common_words)
        plt.figure(figsize=(10, 6))
        plt.bar(words_list, counts, color='skyblue', edgecolor='navy')
        plt.title('Top 10 Frequent Words')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('bot_chart.png')
        plt.close() # Important: close plot to prevent memory leaks

    return sentences_count, len(filtered_words), mood, sentiment

# --- BOT HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 **Hello! I am your Text Analyzer Bot.**\n\n"
        "Options:\n"
        "1️⃣ Send me a **.txt file** for deep analysis.\n"
        "2️⃣ Just **type or paste text** directly in the chat.\n\n"
        "I will provide sentiment score and a frequency chart!"
    )
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message(F.document)
async def handle_document(message: types.Message):
    """Handles .txt file uploads."""
    if not message.document.file_name.endswith('.txt'):
        await message.answer("❌ Error: Please send only **.txt** files.")
        return

    await message.answer("📥 Processing file... please wait.")
    
    # Create downloads folder if not exists
    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{message.document.file_name}"
    
    # Download file
    file_info = await bot.get_file(message.document.file_id)
    await bot.download_file(file_info.file_path, file_path)

    # Read content
    try:
        # Trying UTF-8, fallback to ignore errors for binary-like text
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if len(content.strip()) < 5:
            await message.answer("⚠️ The file is too short for analysis.")
            return

        s_count, w_count, mood, score = process_text_analysis(content)
        
        caption = (
            f"📊 **File Analysis: {message.document.file_name}**\n"
            f"---------------------------\n"
            f"[*] Sentences: {s_count}\n"
            f"[*] Meaningful words: {w_count}\n"
            f"[*] Sentiment: {mood} ({score:.2f})"
        )

        chart = FSInputFile("bot_chart.png")
        await message.answer_photo(chart, caption=caption, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"⚙️ An error occurred during processing: {e}")

@dp.message(F.text & ~F.command)
async def handle_text_message(message: types.Message):
    """Handles direct text messages."""
    if len(message.text) < 10:
        await message.answer("ℹ️ Text is too short. Please send at least 10 characters.")
        return

    # Analyze direct text
    s_count, w_count, mood, score = process_text_analysis(message.text)

    caption = (
        f"📝 **Quick Text Report**\n"
        f"---------------------------\n"
        f"[*] Sentences: {s_count}\n"
        f"[*] Meaningful words: {w_count}\n"
        f"[*] Sentiment: {mood} ({score:.2f})"
    )

    chart = FSInputFile("bot_chart.png")
    await message.answer_photo(chart, caption=caption, parse_mode="Markdown")

# --- MAIN ---

async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")