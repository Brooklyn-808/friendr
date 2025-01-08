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
    st.title("Friendr 👋")
    st.subheader("Welcome to Friendr!")
    st.write("Find a clique with a click!")
    
    if st.button("Login / Sign Up"):
        st.session_state.page = "login"  # Navigate to the login page

# Login/Sign-Up Page
def show_login_page():
    st.title("Login / Sign-Up")
    st.write("Please log in or sign up to continue.")
    
    user_name = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        user = next((u for u in data["profiles"] if u["name"] == user_name), None)
        if user:
            if user.get("password") == password:
                st.session_state.user_id = user["id"]
                st.session_state.page = "swipe"  # Navigate to swipe page
                st.success("Logged in successfully!")
            else:
                st.error("Incorrect password.")
        else:
            st.error("User not found.")

    if st.button("Sign Up"):
        if user_name and password:
            new_user_id = str(uuid.uuid4())
            new_user = {
                "id": new_user_id,
                "name": user_name,
                "password": password,
                "age": 18,
                "interests": [],
                "bio": "",
            }
            data["profiles"].append(new_user)
            save_data(data)
            st.session_state.user_id = new_user_id
            st.session_state.page = "swipe"
            st.success("Sign-up successful!")
        else:
            st.error("Please fill in both fields.")

# Profile and Swiping Page
def show_swipe_page():
    st.title("Friendr 👋")
    user_id = st.session_state.user_id
    user_profile = next((p for p in data["profiles"] if p["id"] == user_id), None)
    
    if not user_profile:
        st.error("User profile not found.")
        return

    # Sidebar for editing profile and navigation
    with st.sidebar:
        st.title("Your Profile")
        user_name = st.text_input("Name", user_profile["name"], key="profile_name")
        user_age = st.number_input("Age", min_value=13, max_value=100, value=user_profile.get("age", 18), key="profile_age")
        user_interests = st.text_input("Interests (comma-separated)", ", ".join(user_profile["interests"]), key="profile_interests")
        user_bio = st.text_area("Bio", user_profile.get("bio", ""), key="profile_bio")
        
        if st.button("Save Profile"):
            user_profile.update({
                "name": user_name,
                "age": user_age,
                "interests": [i.strip() for i in user_interests.split(",")],
                "bio": user_bio,
            })
            save_data(data)
            st.success("Profile updated!")

        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.page = "home"  # Navigate to home page
        
        if st.button("Liked Profiles"):
            st.session_state.page = "liked_profiles"  # Navigate to liked profiles
        
        if st.button("Notifications"):
            st.session_state.page = "notifications"  # Navigate to notifications

    # Main swiping area
    profiles = [p for p in data["profiles"] if p["id"] != user_id]
    if profiles:
        if st.session_state.current_index < len(profiles):
            profile = profiles[st.session_state.current_index]
            display_profile(profile)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Like", key=f"like_{st.session_state.current_index}"):
                    if user_id not in data["likes"]:
                        data["likes"][user_id] = []
                    data["likes"][user_id].append(profile["id"])
                    if profile["id"] not in data["notifications"]:
                        data["notifications"][profile["id"]] = []
                    data["notifications"][profile["id"]].append(f"{user_profile['name']} liked your profile!")
                    save_data(data)
                    st.session_state.current_index += 1
            with col2:
                if st.button("👎 Skip", key=f"skip_{st.session_state.current_index}"):
                    st.session_state.current_index += 1
        else:
            st.write("No more profiles to swipe!")
    else:
        st.write("No profiles available.")

# Liked Profiles Page
def show_liked_profiles():
    st.title("Liked Profiles")
    show_back_button()  # Back button

    user_id = st.session_state.user_id
    liked_profiles = [p for p in data["profiles"] if p["id"] in data["likes"].get(user_id, [])]
    
    if liked_profiles:
        for profile in liked_profiles:
            st.write("---")
            display_profile(profile)
    else:
        st.write("You haven't liked any profiles yet.")

# Notifications Page
def show_notifications_page():
    st.title("Notifications")
    show_back_button()  # Back button

    show_notifications()

# Chat Page
def show_chat_page():
    st.title("Chat with Matches")
    show_back_button()  # Back button
    
    user_id = st.session_state.user_id
    user_profile = next((p for p in data["profiles"] if p["id"] == user_id), None)
    
    # Check mutual likes
    mutual_matches = [
        p for p in data["profiles"] if user_id in data["likes"].get(p["id"], []) and p["id"] in data["likes"].get(user_id, [])
    ]
    
    if mutual_matches:
        for match in mutual_matches:
            st.write(f"### Chat with {match['name']}")
            if match["id"] not in data["messages"]:
                data["messages"][match["id"]] = []
            chat_history = data["messages"][match["id"]]
            
            # Show chat history
            for msg in chat_history:
                st.write(msg)
            
            # Send message
            message = st.text_input("Type your message here", key=f"message_{match['id']}")
            if st.button(f"Send to {match['name']}", key=f"send_{match['id']}"):
                if message:
                    data["messages"][match["id"]].append(f"{user_profile['name']}: {message}")
                    save_data(data)
                    st.success("Message sent!")
                else:
                    st.error("Please type a message.")
    else:
        st.write("You have no mutual matches to chat with.")
        
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
