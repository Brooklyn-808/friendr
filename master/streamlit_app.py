import streamlit as st
import random

# App title
st.title("Friendr 👋")
st.subheader("Swipe and connect with new friends!")

# Fake database for user profiles
profiles = [
    {"name": "Alice", "age": 25, "interests": ["Hiking", "Music", "Art"], "bio": "Lover of all things nature."},
    {"name": "Bob", "age": 28, "interests": ["Gaming", "Tech", "Cooking"], "bio": "Always up for a co-op game or a cooking session!"},
    {"name": "Charlie", "age": 23, "interests": ["Reading", "Travel", "Photography"], "bio": "Capturing moments one photo at a time."},
    {"name": "Daisy", "age": 27, "interests": ["Yoga", "Gardening", "Cooking"], "bio": "Looking for someone to exchange plant tips!"},
    {"name": "Ethan", "age": 22, "interests": ["Running", "Movies", "Coding"], "bio": "Marathon runner and a movie geek."},
]

# Sidebar for user profile
st.sidebar.title("Create Your Profile")
user_name = st.sidebar.text_input("Your Name", "")
user_age = st.sidebar.number_input("Your Age", min_value=13, max_value=100, value=18)
user_interests = st.sidebar.text_input("Your Interests (comma-separated)", "")
user_bio = st.sidebar.text_area("Your Bio", "")

if st.sidebar.button("Save Profile"):
    if user_name and user_interests:
        profiles.append({
            "name": user_name,
            "age": user_age,
            "interests": [i.strip() for i in user_interests.split(",")],
            "bio": user_bio,
        })
        st.sidebar.success("Profile saved! You can now swipe on friends.")
    else:
        st.sidebar.error("Please fill in your name and interests!")

# Initialize session state for swiping
if "index" not in st.session_state:
    st.session_state.index = 0
if "liked" not in st.session_state:
    st.session_state.liked = []

# Swipe functionality
if st.session_state.index < len(profiles):
    profile = profiles[st.session_state.index]
    st.write(f"### {profile['name']} ({profile['age']} years old)")
    st.write(f"**Interests:** {', '.join(profile['interests'])}")
    st.write(f"**Bio:** {profile['bio']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Like"):
            st.session_state.liked.append(profile)
            st.session_state.index += 1
    with col2:
        if st.button("👎 Skip"):
            st.session_state.index += 1
else:
    st.write("No more profiles to swipe!")
    if len(st.session_state.liked) > 0:
        st.write("### People you liked:")
        for liked_profile in st.session_state.liked:
            st.write(f"- **{liked_profile['name']}** ({liked_profile['age']} years old)")
    else:
        st.write("You haven't liked anyone yet. 😔")
