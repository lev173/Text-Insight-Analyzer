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

# Custom imports
from db_manager import init_db, register_user, log_analysis, get_user_stats, get_leaderboard, get_full_history_df
from news_parser import get_tech_news

# --- CONFIG ---
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
nltk.download('punkt')
nltk.download('stopwords')

def process_text_analysis(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity 
    clean_text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    words = nltk.word_tokenize(clean_text)
    stop_words = set(stopwords.words('english')) | set(stopwords.words('russian'))
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]

    word_counts = Counter(filtered_words)
    common_words = word_counts.most_common(10)
    mood = "Positive 😊" if sentiment > 0.1 else "Negative 😟" if sentiment < -0.1 else "Neutral 😐"

    if common_words:
        words_list, counts = zip(*common_words)
        plt.figure(figsize=(10, 6))
        plt.bar(words_list, counts, color='skyblue')
        plt.title('Analysis Result')
        plt.savefig('bot_chart.png')
        plt.close()

    return len(blob.sentences), len(filtered_words), mood, sentiment

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🚀 **AI News & Text Analyzer is Ready!**\n\nCommands:\n/news - Get & analyze tech news\n/top - Leaderboard\n/export - Get Excel report")

@dp.message(Command("news"))
async def cmd_news(message: types.Message):
    msg = await message.answer("🌐 Fetching latest tech news from Hacker News...")
    headlines = get_tech_news()
    
    if not headlines:
        await msg.edit_text("❌ Error fetching news. Please try again later.")
        return

    full_text = ". ".join(headlines)
    _, _, mood, score = process_text_analysis(full_text)
    
    # Save this analysis to DB for the bot owner
    log_analysis(message.from_user.id, score)

    response = (
        f"🆕 **Latest Tech News Sentiment**\n"
        f"Overall Mood: **{mood}** ({score:.2f})\n\n"
        f"**Top Headlines:**\n"
    )
    for i, title in enumerate(headlines, 1):
        response += f"{i}. {title}\n"

    chart = FSInputFile("bot_chart.png")
    await message.answer_photo(chart, caption=response)

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    leaders = get_leaderboard()
    text = "🏆 **Leaderboard:**\n" + "\n".join([f"{i+1}. @{u} - {c} reqs" for i, (u, c) in enumerate(leaders)])
    await message.answer(text)

@dp.message(F.text & ~F.command)
async def handle_text(message: types.Message):
    register_user(message.from_user.id, message.from_user.username)
    _, _, mood, score = process_text_analysis(message.text)
    log_analysis(message.from_user.id, score)
    chart = FSInputFile("bot_chart.png")
    await message.answer_photo(chart, caption=f"Sentiment: {mood} ({score:.2f})")

async def main():
    init_db()
    print("System Online...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())