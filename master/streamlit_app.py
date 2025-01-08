import streamlit as st
import json
import os

# File to store user profiles, likes, and messages
DATA_FILE = "profiles.json"

# Load profiles from JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    else:
        return {"profiles": [], "likes": {}, "messages": {}}

# Save profiles to JSON
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Initialize data
data = load_data()

# App title
st.title("Friendr 👋")
st.subheader("Swipe, Match, and Chat with New Friends!")

# Check if the user has created a profile
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "chat_with" not in st.session_state:
    st.session_state.chat_with = None

# Function to display a single profile
def display_profile(profile):
    st.image("https://via.placeholder.com/400", width=300, caption="Profile Picture")
    st.write(f"### {profile['name']} ({profile['age']} years old)")
    st.write(f"**Interests:** {', '.join(profile['interests'])}")
    st.write(f"**Bio:** {profile['bio']}")

# Profile creation/edit sidebar
if st.sidebar.button("Create/Edit Profile") or st.session_state.user_profile is None:
    st.sidebar.title("Create/Edit Your Profile")
    user_name = st.sidebar.text_input("Your Name", st.session_state.user_profile["name"] if st.session_state.user_profile else "")
    user_age = st.sidebar.number_input("Your Age", min_value=13, max_value=100, value=18)
    user_interests = st.sidebar.text_input("Your Interests (comma-separated)", 
                                           ", ".join(st.session_state.user_profile["interests"]) if st.session_state.user_profile else "")
    user_bio = st.sidebar.text_area("Your Bio", st.session_state.user_profile["bio"] if st.session_state.user_profile else "")

    if st.sidebar.button("Save Profile"):
        if user_name and user_interests:
            st.session_state.user_profile = {
                "name": user_name,
                "age": user_age,
                "interests": [i.strip() for i in user_interests.split(",")],
                "bio": user_bio,
            }
            # Add the user profile to the global profiles list (or update if already exists)
            user_found = False
            for profile in data["profiles"]:
                if profile["name"] == user_name:
                    profile.update(st.session_state.user_profile)
                    user_found = True
                    break
            if not user_found:
                data["profiles"].append(st.session_state.user_profile)
            save_data(data)
            st.sidebar.success("Profile saved!")
        else:
            st.sidebar.error("Please fill in all required fields!")

# Main app: Swipe functionality
if st.session_state.user_profile:
    st.write("### Browse Friends")
    profiles = [p for p in data["profiles"] if p["name"] != st.session_state.user_profile["name"]]

    # Check if someone liked the user
    user = st.session_state.user_profile["name"]
    liked_by_others = [u for u, liked_users in data["likes"].items() if user in liked_users]
    if liked_by_others:
        st.info(f"You've been liked by: {', '.join(liked_by_others)}")

    # Show mutual matches and chat option
    if user in data["likes"]:
        mutual_matches = [u for u in data["likes"][user] if user in data["likes"].get(u, [])]
        if mutual_matches:
            st.write("### Mutual Matches")
            for match in mutual_matches:
                if st.button(f"Chat with {match}"):
                    st.session_state.chat_with = match

    if st.session_state.chat_with:
        st.write(f"### Chat with {st.session_state.chat_with}")
        chat_key = tuple(sorted([user, st.session_state.chat_with]))
        if chat_key not in data["messages"]:
            data["messages"][chat_key] = []

        # Display chat messages
        for message in data["messages"][chat_key]:
            sender, text = message
            st.write(f"**{sender}:** {text}")

        # Send a new message
        new_message = st.text_input("Write a message:")
        if st.button("Send"):
            if new_message:
                data["messages"][chat_key].append((user, new_message))
                save_data(data)
                st.success("Message sent!")
    
    # Swipe functionality
    if st.session_state.current_index < len(profiles):
        profile = profiles[st.session_state.current_index]
        display_profile(profile)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Like"):
                # Save like to JSON
                if user not in data["likes"]:
                    data["likes"][user] = []
                data["likes"][user].append(profile["name"])
                save_data(data)
                st.session_state.current_index += 1
        with col2:
            if st.button("👎 Skip"):
                st.session_state.current_index += 1
    else:
        st.write("No more profiles to swipe! Come back later. 😊")
else:
    st.write("Please create your profile to start swiping.")
