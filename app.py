import streamlit as st
import pandas as pd
import sqlite3
from hashlib import sha256

# --- DB Setup ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
''')
conn.commit()

# --- Helper Functions ---
def hash_password(password):
    return sha256(password.encode()).hexdigest()

def verify_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    return cursor.fetchone()

def create_user(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

@st.cache_data
def load_songs():
    df = pd.read_excel("songs.xlsx")
    df.dropna(subset=["Genre", "Title"], inplace=True)
    return df

def get_suggestions(user_genre, all_genres):
    return [g for g in all_genres if g != user_genre][:3]

# --- UI ---
st.set_page_config(page_title="Streamify", layout="wide")
st.markdown("<h1 style='color:#1DB954;'>🎵 Streamify - Smart Music Suggester</h1>", unsafe_allow_html=True)

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Select Action", menu)

# Login
if choice == "Login":
    st.sidebar.subheader("Login Section")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        if verify_user(username, password):
            st.success(f"Welcome {username} 👋")
            songs_df = load_songs()
            genres = songs_df["Genre"].unique().tolist()

            st.subheader("🎧 Choose Your Favorite Genre")
            selected_genre = st.selectbox("Select Genre", genres)

            filtered_songs = songs_df[songs_df["Genre"] == selected_genre]
            st.write(f"Showing {len(filtered_songs)} songs in **{selected_genre}** genre:")
            st.table(filtered_songs[["Title", "Artist "]])

            # If user listens to 5+ songs in one genre, suggest others
            if len(filtered_songs) >= 5:
                st.warning("You've explored a lot of this genre! Try something new 🎶")
                st.subheader("🌟 Suggested Genres to Explore")
                suggestions = get_suggestions(selected_genre, genres)
                for g in suggestions:
                    st.markdown(f"- {g}")
        else:
            st.error("Invalid credentials. Try again.")

# Register
elif choice == "Register":
    st.sidebar.subheader("Create New Account")
    new_user = st.sidebar.text_input("Username")
    new_pass = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Register"):
        if create_user(new_user, new_pass):
            st.success("Account created successfully!")
        else:
            st.error("Username already exists. Try a different one.")
