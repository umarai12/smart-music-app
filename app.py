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
    return [g for g in all_genres if g not in user_genre][:3]

# --- UI Setup ---
st.set_page_config(page_title="Streamify", layout="wide")
st.markdown("<h1 style='color:#1DB954;'>🎵 Streamify - Smart Music Suggester</h1>", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Register ---
if not st.session_state.logged_in:
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Select Action", menu)

    if choice == "Login":
        st.sidebar.subheader("Login Section")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        login_btn = st.sidebar.button("Login")

        if login_btn:
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username} 👋")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials. Try again.")

    elif choice == "Register":
        st.sidebar.subheader("Create New Account")
        new_user = st.sidebar.text_input("Username")
        new_pass = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Register"):
            if create_user(new_user, new_pass):
                st.success("Account created successfully!")
            else:
                st.error("Username already exists. Try a different one.")

# --- Main App ---
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    logout_btn = st.sidebar.button("Logout")
    if logout_btn:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

    songs_df = load_songs()
    genres = sorted(songs_df["Genre"].dropna().unique().tolist())

    st.subheader("🎧 Choose Your Favorite Genres")
    selected_genres = st.multiselect("Select Genre(s)", genres)

    if selected_genres:
        filtered_songs = songs_df[songs_df["Genre"].isin(selected_genres)]
        st.write(f"Showing {len(filtered_songs)} songs for selected genres:")
        st.table(filtered_songs[["Title", "Artist"]])

        for genre in selected_genres:
            genre_count = len(filtered_songs[filtered_songs["Genre"] == genre])
            if genre_count >= 5:
                st.warning(f"You’ve explored many songs in '{genre}'! Try exploring other genres too 🎶")

        st.subheader("🌟 Suggested Genres to Explore")
        suggestions = get_suggestions(selected_genres, genres)
        if suggestions:
            for g in suggestions:
                st.markdown(f"- {g}")
        else:
            st.info("You're already exploring all genres!")
    else:
        st.info("Please select at least one genre to view songs.")
