import requests
from datetime import datetime
import streamlit as st
import uuid
import json
import os
import time
# Flask URL (replace with your actual Flask URL)
FLASK_URL = "http://your-flask-server-url:5000"  # Update with your Flask URL
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

# Helper function to display a profile with multiple images
def display_profile(profile):
    # Show profile images as a slideshow
    image_urls = profile.get("image_urls", [])
    if image_urls:
        for i, url in enumerate(image_urls):
            st.image(url, width=300, caption=f"Profile Picture {i + 1}")
            time.sleep(5)
    else:
        st.image("https://via.placeholder.com/400", width=300, caption="Profile Picture")
    
    st.write(f"### {profile['name']} ({profile['age']} years old)")
    st.write(f"**Interests:** {', '.join(profile['interests'])}")
    st.write(f"**Bio:** {profile['bio']}")

# Back Button
def show_back_button():
    if st.button("Back"):
        st.session_state.page = "swipe"  # Go back to the swiping page

# Notifications Section
def show_notifications():
    user_id = st.session_state.user_id
    if user_id and user_id in data["notifications"]:
        st.sidebar.subheader("Notifications")
        notifications = data["notifications"][user_id]
        for i, notification in enumerate(notifications):
            st.sidebar.write(notification)
            if st.sidebar.button(f"Dismiss Notification {i + 1}", key=f"dismiss_{i}"):
                data["notifications"][user_id].remove(notification)
                save_data(data)

# Home Page
def show_home_page():
    st.title("Welcome to the Chat App!")
    if st.button("Login"):
        st.session_state.page = "login"

# Login Page
def show_login_page():
    st.title("Login")
    user_id = st.text_input("Enter your user ID")
    if user_id and user_id not in [profile['id'] for profile in data["profiles"]]:
        st.error("User ID does not exist.")
    elif user_id:
        st.session_state.user_id = user_id
        st.session_state.page = "swipe"

# Swipe Page (where users browse profiles)
def show_swipe_page():
    st.title("Swipe through Profiles")
    show_notifications()  # Show notifications on the sidebar
    
    user_id = st.session_state.user_id
    profiles = data["profiles"]
    current_index = st.session_state.current_index

    if current_index < len(profiles):
        profile = profiles[current_index]
        display_profile(profile)
        
        if st.button("Like"):
            if user_id not in data["likes"]:
                data["likes"][user_id] = []
            data["likes"][user_id].append(profile["id"])
            save_data(data)
        
        if st.button("Pass"):
            st.session_state.current_index += 1
        
    else:
        st.write("No more profiles to view.")
    
    if st.button("View Liked Profiles"):
        st.session_state.page = "liked_profiles"

# Liked Profiles Page
def show_liked_profiles():
    st.title("Your Liked Profiles")
    show_back_button()
    
    user_id = st.session_state.user_id
    liked_profiles = data["likes"].get(user_id, [])
    
    if liked_profiles:
        for liked_id in liked_profiles:
            profile = next((p for p in data["profiles"] if p["id"] == liked_id), None)
            if profile:
                display_profile(profile)
                if st.button(f"Chat with {profile['name']}"):
                    st.session_state.chat_with = profile["id"]
                    st.session_state.page = "chat"
    else:
        st.write("You haven't liked any profiles yet.")

# Notifications Page
def show_notifications_page():
    st.title("Notifications")
    show_notifications()

# Function to get chat messages from Flask backend
def get_chat_messages(sender, receiver):
    response = requests.get(f"{FLASK_URL}/get_messages", params={"sender": sender, "receiver": receiver})
    if response.status_code == 200:
        return response.json()
    return []

# Function to send a chat message through Flask backend
def send_chat_message(sender, receiver, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "timestamp": timestamp
    }
    response = requests.post(f"{FLASK_URL}/send_message", json=payload)
    if response.status_code == 200:
        return True
    return False

# Chat Page
def show_chat_page():
    st.title("Chat with Matches")
    show_back_button()  # Function for the back button (if necessary)

    # Get user and match profiles
    user_id = st.session_state.user_id
    chat_with = st.session_state.chat_with
    user_profile = next((p for p in data["profiles"] if p["id"] == user_id), None)
    match_profile = next((p for p in data["profiles"] if p["id"] == chat_with), None)

    if not match_profile:
        st.error("User not found.")
        return

    # Fetch chat history from Flask backend
    messages = get_chat_messages(user_id, chat_with)
    
    # Create an empty container for the chat history
    chat_container = st.empty()

    # Display the chat history in a scrollable text box
    chat_history = "\n".join([f"{message['sender']}: {message['message']}" for message in messages])  # Format messages
    
    chat_container.text_area("Chat History", value=chat_history, height=300, max_chars=None, disabled=True)

    # Check if we already have a value for the message in the session state
    message_key = f"message_{match_profile['id']}"
    if message_key not in st.session_state:
        st.session_state[message_key] = ""  # Initialize empty message field

    # Display the text input field using session state value
    message = st.text_input("Type your message here", value=st.session_state[message_key], key=message_key)

    # Send button
    if st.button(f"Send to {match_profile['name']}", key=f"send_{match_profile['id']}"):
        if message:
            # Send the message through Flask
            success = send_chat_message(user_id, chat_with, message)
            if success:
                st.success("Message sent")
                st.session_state[message_key] = ""  # Clear input field
                st.experimental_rerun()  # Refresh the page to show updated messages
            else:
                st.error("Failed to send message.")
        else:
            st.error("Please type a message.")
    
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
