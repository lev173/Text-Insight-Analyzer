import streamlit as st
import pandas as pd
import sqlite3
from textblob import TextBlob
from db_manager import DB_NAME, get_leaderboard

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Insight Dashboard", page_icon="🌐", layout="wide")

st.title("🌐 AI Insight: Global Analytics Dashboard")
st.markdown("Monitoring user activity and global news sentiment in real-time.")

# --- DATABASE CONNECTION ---
def get_connection():
    return sqlite3.connect(DB_NAME)

# --- SIDEBAR: GLOBAL METRICS ---
st.sidebar.header("Global Metrics")
conn = get_connection()

try:
    total_users = pd.read_sql_query("SELECT COUNT(*) as count FROM users", conn).iloc[0]['count']
    total_logs = pd.read_sql_query("SELECT COUNT(*) as count FROM analysis_logs", conn).iloc[0]['count']
    avg_sentiment = pd.read_sql_query("SELECT AVG(sentiment_score) as avg FROM analysis_logs", conn).iloc[0]['avg']
    
    st.sidebar.metric("Total Users", total_users)
    st.sidebar.metric("Total Analyses", total_logs)
    st.sidebar.metric("Average Mood Score", f"{avg_sentiment:.2f}" if avg_sentiment else "0.0")
except:
    st.sidebar.warning("Database is empty or initializing...")

# --- MAIN LAYOUT: TWO COLUMNS ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🏆 Leaderboard")
    leaders = get_leaderboard()
    if leaders:
        df_leaders = pd.DataFrame(leaders, columns=["User", "Requests"])
        st.dataframe(df_leaders, use_container_width=True)
    else:
        st.info("No users registered yet.")

with col_right:
    st.subheader("📈 Sentiment Over Time")
    query = "SELECT timestamp, sentiment_score FROM analysis_logs ORDER BY timestamp ASC"
    df_trends = pd.read_sql_query(query, conn)
    
    if not df_trends.empty:
        df_trends['timestamp'] = pd.to_datetime(df_trends['timestamp'])
        st.line_chart(df_trends.set_index('timestamp'))
    else:
        st.info("Not enough data to build a trend chart.")

# --- SECTION 3: LIVE NEWS FEED & ANALYSIS ---
st.divider()
st.subheader("📰 Live Intelligence Testing")

tab1, tab2 = st.tabs(["Manual Analysis", "Database Inspection"])

with tab1:
    user_input = st.text_area("Analyze any text (or paste news article):", placeholder="Enter text here...")
    if st.button("Run AI Analysis"):
        if user_input:
            blob = TextBlob(user_input)
            score = blob.sentiment.polarity
            
            m1, m2 = st.columns(2)
            m1.metric("Sentiment Score", f"{score:.2f}")
            if score > 0.1: m2.success("Positive Mood 😊")
            elif score < -0.1: m2.error("Negative Mood 😟")
            else: m2.warning("Neutral Mood 😐")
        else:
            st.warning("Please enter text first.")

with tab2:
    st.subheader("🔍 Raw Activity Log")
    df_raw = pd.read_sql_query("SELECT * FROM analysis_logs ORDER BY timestamp DESC LIMIT 50", conn)
    st.write(df_raw)

conn.close()