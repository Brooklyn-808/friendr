import streamlit as st
import uuid
import json
import os

# File to store user profiles and messages
DATA_FILE = "profiles.json"

# Load profiles from JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    else:
        return {"profiles": [], "likes": {}, "messages": {}, "notifications": {}}

# Save profiles to JSON
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Initialize data
data = load_data()

# Initialize session state variables
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "home"  # Default page
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "chat_with" not in st.session_state:
    st.session_state.chat_with = None

# Helper function to display a profile
def display_profile(profile):
    st.image("https://via.placeholder.com/400", width=300, caption="Profile Picture")
    st.write(f"### {profile['name']} ({profile['age']} years old)")
    st.write(f"**Interests:** {', '.join(profile['interests'])}")
    st.write(f"**Bio:** {profile['bio']}")

# Back Button
def show_back_button():
    if st.button("Back"):
        st.session_state.page = "swipe"  # Go back to the swiping page

# Chat Page
def show_chat_page():
    st.title("Chat with Mutual Matches")
    user_id = st.session_state.user_id
    user_profile = next((p for p in data["profiles"] if p["id"] == user_id), None)

    if not user_profile:
        st.error("User profile not found.")
        return

    # Show the Back button
    show_back_button()

    # Find mutual likes
    mutual_likes = []
    for liked_profile_id in data["likes"].get(user_id, []):
        if user_id in data["likes"].get(liked_profile_id, []):
            mutual_likes.append(liked_profile_id)

    if not mutual_likes:
        st.write("You don't have any mutual matches yet.")
        return

    # Show a list of mutual matches
    st.write("### You have mutual matches with:")
    for mutual_profile_id in mutual_likes:
        profile = next(p for p in data["profiles"] if p["id"] == mutual_profile_id)
        st.write(f"**{profile['name']}** - {profile['bio']}")
        if st.button(f"Chat with {profile['name']}", key=f"chat_{mutual_profile_id}"):
            st.session_state.chat_with = mutual_profile_id
            st.session_state.page = "chat_with"  # Navigate to the chat page for that match

# Chat Interface
def show_chat_with_page():
    st.title("Chat")
    chat_with_id = st.session_state.chat_with
    user_id = st.session_state.user_id
    user_profile = next((p for p in data["profiles"] if p["id"] == user_id), None)
    chat_with_profile = next((p for p in data["profiles"] if p["id"] == chat_with_id), None)

    if not chat_with_profile:
        st.error("User not found for chat.")
        return

    # Show the Back button
    show_back_button()

    # Create or load the messages for the chat
    if chat_with_id not in data["messages"]:
        data["messages"][chat_with_id] = {}

    if user_id not in data["messages"][chat_with_id]:
        data["messages"][chat_with_id][user_id] = []

    # Show chat history
    st.write(f"### Chat with {chat_with_profile['name']}")
    messages = data["messages"][chat_with_id][user_id]
    for message in messages:
        st.write(f"{message['sender']}: {message['text']}")

    # Send a new message
    message_input = st.text_input("Type your message", key="message_input")
    if st.button("Send Message"):
        if message_input:
            message = {
                "sender": user_profile['name'],
                "text": message_input
            }
            # Add the message to the chat
            data["messages"][chat_with_id][user_id].append(message)
            save_data(data)  # Save messages to data file
            st.session_state.page = "chat_with"  # Stay on the chat page to see the new message

# Routing logic
if st.session_state.page == "home":
    show_home_page()
elif st.session_state.page == "login":
    show_login_page()
elif st.session_state.page == "swipe":
    show_swipe_page()
elif st.session_state.page == "liked_profiles":
    show_liked_profiles()
elif st.session_state.page == "notifications":
    show_notifications_page()
elif st.session_state.page == "chat":
    show_chat_page()
elif st.session_state.page == "chat_with":
    show_chat_with_page()
