import streamlit as st
import pandas as pd

# Load Excel file
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("songs.xlsx")
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

# Load the data
songs_df = load_data()

# Check if data loaded correctly
if songs_df.empty:
    st.stop()

# Page title
st.title("🎵 Smart Music Recommender")

# Show genre options
genres = songs_df["Genre"].dropna().unique().tolist()
user_genres = st.multiselect("Select your preferred genre(s):", genres)

# Track user preferences in session
if 'genre_count' not in st.session_state:
    st.session_state.genre_count = {}

for genre in user_genres:
    st.session_state.genre_count[genre] = st.session_state.genre_count.get(genre, 0) + 1

# Recommend songs
if user_genres:
    st.subheader("🎧 Songs Recommended for You:")
    recommended = songs_df[songs_df["Genre"].isin(user_genres)].sample(n=5, replace=True)
    for index, row in recommended.iterrows():
        st.write(f"• {row['Song Name']} by {row['Artist']} ({row['Genre']})")

# Suggest alternative genres if user listens to same genre too much
most_selected = max(st.session_state.genre_count.values()) if st.session_state.genre_count else 0
if most_selected >= 5:
    st.warning("You've been listening to one genre a lot! Try exploring something new 🎶")
    other_genres = [g for g in genres if g not in user_genres]
    if other_genres:
        st.write("Try these genres:")
        st.write(", ".join(other_genres))
