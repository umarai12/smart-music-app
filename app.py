import streamlit as st
import pandas as pd
import json
import os

# Load or create user data
USER_FILE = "users.json"
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

# Load songs dataset
@st.cache_data
def load_songs():
    try:
        df = pd.read_excel("songs.xlsx")
        return df
    except Exception as e:
        st.error(f"Error loading songs: {e}")
        return pd.DataFrame()

songs_df = load_songs()

# Auth system
def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = {"password": password, "preferences": []}
    save_users(users)
    return True

def authenticate(username, password):
    users = load_users()
    return username in users and users[username]["password"] == password

def update_preferences(username, selected_genres):
    users = load_users()
    if username in users:
        users[username]["preferences"].extend(selected_genres)
        users[username]["preferences"] = list(set(users[username]["preferences"]))
        save_users(users)

def suggest_genres(preferences):
    # If user listens to one genre too much, suggest alternatives
    if not preferences:
        return []
    genre_count = pd.Series(preferences).value_counts()
    top_genre = genre_count.idxmax()
    if genre_count[top_genre] >= 5:
        return list(set(songs_df["Genre"].unique()) - set([top_genre]))
    return []

# Streamlit app
st.title("🎧 Smart Music Suggestion App")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if st.session_state.logged_in_user:
    st.success(f"Logged in as {st.session_state.logged_in_user}")
    
    st.subheader("🎵 Choose Your Preferred Genres")
    genres = songs_df["Genre"].dropna().unique().tolist()
    selected_genres = st.multiselect("Select genres you like to listen to:", genres)

    if st.button("Save Preferences"):
        update_preferences(st.session_state.logged_in_user, selected_genres)
        st.success("Preferences saved.")

    users = load_users()
    prefs = users[st.session_state.logged_in_user]["preferences"]
    
    st.markdown(f"Your preferences: {prefs}")

    if prefs:
        suggestion = suggest_genres(prefs)
        if suggestion:
            st.warning("You are listening to one genre too much. Try these:")
            st.write(suggestion)

    st.subheader("🎧 Songs You Might Like")
    filtered = songs_df[songs_df["Genre"].isin(prefs)]
    if not filtered.empty:
        st.dataframe(filtered[["Title", "Artist", "Genre"]])
    else:
        st.info("No songs found for selected preferences.")

    if st.button("Logout"):
        st.session_state.logged_in_user = None
        st.experimental_rerun()

elif choice == "Register":
    st.subheader("Create New Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if register_user(username, password):
            st.success("Registered successfully. Please log in.")
        else:
            st.error("User already exists.")

elif choice == "Login":
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.success("Login successful.")
            st.session_state.logged_in_user = username
            st.experimental_rerun()
        else:
            st.error("Invalid credentials.")
