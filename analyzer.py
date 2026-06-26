import os
import re
import string
from collections import Counter

# Настройка бэкенда Matplotlib для фоновой генерации картинок без открытия окон
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pandas as pd
from textblob import TextBlob

# Локальный список стоп-слов (гарантирует 100% автономность работы без сбоев NLTK)
STOP_WORDS = {
    'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were', 'it', 'this', 'that', 'i', 'you', 'he', 'she', 'they', 'we'},
    'ru': {'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только'}
}

class AdvancedTextAnalyzer:
    def __init__(self):
        # Объединяем стоп-слова для мультиязычной фильтрации
        self.stop_words = STOP_WORDS['en'] | STOP_WORDS['ru']

    def _clean_and_tokenize(self, text: str) -> list:
        """Очищает текст от пунктуации и разбивает на слова (взамен nltk.word_tokenize)."""
        # Удаляем пунктуацию через translate, как в твоем исходном коде
        clean_text = text.translate(str.maketrans('', '', string.punctuation)).lower()
        # Извлекаем слова с поддержкой кириллицы и латиницы
        words = re.findall(r'\b[a-zA-Zа-яА-ЯёЁ]+\b', clean_text)
        # Фильтруем стоп-слова и короткие токены
        return [w for w in words if w not in self.stop_words and len(w) > 2]

    def plot_statistics(self, common_words: list, output_path: str = 'word_frequency_chart.png'):
        """Создает бар-чарт частоты слов и сохраняет его на диск без вызова plt.show()."""
        if not common_words:
            return
        
        words, counts = zip(*common_words)
        
        plt.figure(figsize=(10, 6))
        plt.bar(words, counts, color='skyblue', edgecolor='navy')
        plt.title('Top 10 Most Frequent Words', fontsize=14)
        plt.xlabel('Words', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Сохраняем график в файл. Благодаря 'Agg' это работает в фоне
        plt.savefig(output_path, dpi=150)
        plt.close() # Высвобождаем оперативную память устройства
        print(f"[*] Visualization saved as '{output_path}'")

    def process_text_data(self, text: str, source_name: str = "Raw Text") -> dict:
        """Основная логика анализа текста (подходит и для файлов, и для бота)."""
        if not text.strip():
            return {}

        # Структурный и эмоциональный анализ через TextBlob
        blob = TextBlob(text)
        sentences_count = len(blob.sentences)
        sentiment = blob.sentiment.polarity 

        # Очистка и подсчет частоты слов
        filtered_words = self._clean_and_tokenize(text)
        word_counts = Counter(filtered_words)
        common_words = word_counts.most_common(10)

        # Интерпретация тональности
        mood = "Neutral"
        if sentiment > 0.1: 
            mood = "Positive"
        elif sentiment < -0.1: 
            mood = "Negative"

        # Формируем структурированный отчет для вывода
        report = {
            "source": source_name,
            "sentences_count": sentences_count if sentences_count > 0 else 1,
            "words_cleaned_count": len(filtered_words),
            "sentiment_score": round(sentiment, 2),
            "mood": mood,
            "common_words": common_words
        }
        return report

    def analyze_file(self, file_path: str) -> None:
        """Метод для обратной совместимости локального запуска через файлы."""
        text = ""
        encodings = ['utf-8', 'utf-16', 'windows-1251']
        
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as file:
                    text = file.read()
                if text: 
                    break
            except (UnicodeDecodeError, FileNotFoundError):
                continue

        if not text:
            print(f"Error: Could not read file '{file_path}'.")
            return

        # Запускаем обработку данных
        report = self.process_text_data(text, source_name=file_path)
        
        # Консольный вывод (полностью сохраняем твою стилистику)
        print("\n" + "="*45)
        print(f" TEXT ANALYSIS REPORT: {report['source']}")
        print("="*45)
        print(f"[*] Total sentences:     {report['sentences_count']}")
        print(f"[*] Words after cleanup: {report['words_cleaned_count']}")
        print(f"[*] Sentiment Score:    {report['mood']} ({report['sentiment_score']:.2f})")
        print("-" * 45)
        print(" TOP 10 FREQUENT WORDS:")
        
        if report['common_words']:
            df = pd.DataFrame(report['common_words'], columns=['Word', 'Count'])
            print(df.to_string(index=False))
            print("="*45)
            # Генерация инфографики
            self.plot_statistics(report['common_words'])
        else:
            print("Not enough data for word analysis.")
            print("="*45)

if __name__ == "__main__":
    # Локальный самотест скрипта (ищет файл data.txt)
    analyzer = AdvancedTextAnalyzer()
    analyzer.analyze_file("data.txt")
