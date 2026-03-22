import nltk
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
from collections import Counter
import string

# Separate NLTK resource downloads
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

from nltk.corpus import stopwords

def plot_statistics(common_words):
    """Creates a bar chart of the most frequent words."""
    if not common_words:
        return
    
    words, counts = zip(*common_words)
    
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue', edgecolor='navy')
    plt.title('Top 10 Most Frequent Words', fontsize=14)
    plt.xlabel('Words', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save the chart as an image
    plt.savefig('word_frequency_chart.png')
    print("[*] Visualization saved as 'word_frequency_chart.png'")
    plt.show()

def analyze_text(file_path):
    text = ""
    # Handling different encodings for Windows compatibility
    encodings = ['utf-8', 'utf-16', 'windows-1251']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as file:
                text = file.read()
            if text: break
        except (UnicodeDecodeError, FileNotFoundError):
            continue

    if not text:
        print(f"Error: Could not read file '{file_path}'.")
        return

    # Structural and Sentiment Analysis
    blob = TextBlob(text)
    sentences_count = len(blob.sentences)
    sentiment = blob.sentiment.polarity 

    # Text cleaning (removing punctuation and lowering case)
    clean_text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    words = nltk.word_tokenize(clean_text)
    
    # Filtering stop words (English & Russian)
    stop_words = set(stopwords.words('english')) | set(stopwords.words('russian'))
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]

    # Frequency Calculation
    word_counts = Counter(filtered_words)
    common_words = word_counts.most_common(10)
    
    # Console Output
    print("\n" + "="*45)
    print(f" TEXT ANALYSIS REPORT: {file_path}")
    print("="*45)
    print(f"[*] Total sentences:     {sentences_count}")
    print(f"[*] Words after cleanup: {len(filtered_words)}")
    
    # Sentiment interpretation
    mood = "Neutral"
    if sentiment > 0.1: mood = "Positive "
    elif sentiment < -0.1: mood = "Negative "
    
    print(f"[*] Sentiment Score:    {mood} ({sentiment:.2f})")
    print("-" * 45)
    print(" TOP 10 FREQUENT WORDS:")
    
    if common_words:
        df = pd.DataFrame(common_words, columns=['Word', 'Count'])
        print(df.to_string(index=False))
        print("="*45)
        
        # Trigger Visualization
        plot_statistics(common_words)
    else:
        print("Not enough data for word analysis.")
        print("="*45)

if __name__ == "__main__":
    # Ensure 'data.txt' exists in the project folder
    analyze_text("data.txt")