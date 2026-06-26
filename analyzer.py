import os
import re
import string
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pandas as pd
from textblob import TextBlob

STOP_WORDS = {
    'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were', 'it', 'this', 'that', 'i', 'you', 'he', 'she', 'they', 'we'},
    'ru': {'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'это'}
}

# Простой и надежный лексикон для базового анализа русских слов без скачивания гигабайтных моделей
RU_POSITIVE = {'прекрасна', 'прекрасно', 'прекрасный', 'удивительна', 'удивительно', 'любовь', 'радость', 'счастье', 'успех', 'великолепно', 'хорошо', 'мир'}
RU_NEGATIVE = {'плохо', 'ужасно', 'грусть', 'боль', 'ошибка', 'кризис', 'проблема', 'враг', 'ненависть', 'смерть', 'кринж'}

class AdvancedTextAnalyzer:
    def __init__(self):
        self.stop_words = STOP_WORDS['en'] | STOP_WORDS['ru']

    def _clean_and_tokenize(self, text: str) -> list:
        clean_text = text.translate(str.maketrans('', '', string.punctuation)).lower()
        words = re.findall(r'\b[a-zA-Zа-яА-ЯёЁ]+\b', clean_text)
        return [w for w in words if w not in self.stop_words and len(w) > 2]

    def plot_statistics(self, common_words: list, output_path: str = 'word_frequency_chart.png'):
        """Создает горизонтальный бар-чарт, предотвращая наложение слов."""
        if not common_words:
            return
        
        # Разворачиваем список, чтобы самое популярное слово было вверху горизонтального графика
        common_words = common_words[::-1]
        words, counts = zip(*common_words)
        
        plt.figure(figsize=(10, 6))
        # Используем barh для горизонтального отображения
        plt.barh(words, counts, color='#3498db', edgecolor='#2980b9')
        
        plt.title('Top Most Frequent Words', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('Frequency', fontsize=12)
        plt.grid(axis='x', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

    def _analyze_ru_sentiment(self, words: list) -> float:
        """Вычисляет оценку тональности для русскоязычного текста."""
        score = 0.0
        count = 0
        for w in words:
            if w in RU_POSITIVE:
                score += 0.8
                count += 1
            elif w in RU_NEGATIVE:
                score -= 0.8
                count += 1
        return score / count if count > 0 else 0.0

    def process_text_data(self, text: str, source_name: str = "Raw Text") -> dict:
        if not text.strip():
            return {}

        blob = TextBlob(text)
        sentences_count = len(blob.sentences)
        
        # Определяем преобладающий язык по алфавиту
        rus_chars = len(re.findall(r'[а-яА-ЯёЁ]', text))
        eng_chars = len(re.findall(r'[a-zA-Z]', text))
        
        filtered_words = self._clean_and_tokenize(text)
        
        # Выбор алгоритма тональности в зависимости от языка
        if rus_chars > eng_chars:
            sentiment = self._analyze_ru_sentiment(filtered_words)
        else:
            sentiment = blob.sentiment.polarity

        word_counts = Counter(filtered_words)
        common_words = word_counts.most_common(10)

        mood = "Neutral"
        if sentiment > 0.1: 
            mood = "Positive"
        elif sentiment < -0.1: 
            mood = "Negative"

        return {
            "source": source_name,
            "sentences_count": sentences_count if sentences_count > 0 else 1,
            "words_cleaned_count": len(filtered_words),
            "sentiment_score": round(sentiment, 2),
            "mood": mood,
            "common_words": common_words
        }

    def analyze_file(self, file_path: str) -> None:
        text = ""
        encodings = ['utf-8', 'utf-16', 'windows-1251']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as file:
                    text = file.read()
                if text: break
            except (UnicodeDecodeError, FileNotFoundError):
                continue

        if not text:
            return

        report = self.process_text_data(text, source_name=file_path)
        if report['common_words']:
            self.plot_statistics(report['common_words'])

if __name__ == "__main__":
    analyzer = AdvancedTextAnalyzer()
    analyzer.analyze_file("data.txt")
