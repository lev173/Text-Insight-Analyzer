# 📊 Advanced Text Insight Analyzer Bot

An asynchronous Telegram bot built with **Aiogram 3.x** designed for deep linguistic text analysis, automated sentiment tracking, and word frequency visualization.

## 🚀 Features
- **Multilingual Support:** Smart stop-words filtering and metrics evaluation for both English and Russian texts.
- **Sentiment Analysis:** Real-time emotional tone detection (Positive, Negative, Neutral) with custom vocabulary support for accurate Russian speech processing.
- **Background Visuals:** Automatically generates clean, horizontal word frequency bar charts using Matplotlib's 'Agg' backend (headless mode, fully safe for remote servers).
- **In-Memory Optimization:** Generates unique charts per user and immediately clears disk space (`os.remove`) after sending the message.

## 🛠️ Tech Stack
- **Language:** Python 3.11+
- **Bot Framework:** Aiogram 3.x (Asyncio)
- **Data & Analytics:** Pandas, TextBlob, Counter, Regex
- **Visualization:** Matplotlib

## 📦 Installation & Setup

1. Clone the repository:
```bash
git clone [https://github.com/lev173/Text-Insight-Analyzer.git](https://github.com/lev173/Text-Insight-Analyzer.git)
cd Text-Insight-Analyzer
python -m pip install -r requirements.txt\
python bot.py
