import streamlit as st
import json
import os
import uuid

# File to store user profiles and messages
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

# Initialize session state variables
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
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

# Home Page
def show_home_page():
    st.title("Friendr 👋")
    st.subheader("Welcome to Friendr!")
    st.write("Swipe, match, and chat with new friends!")
    if st.button("Login / Sign Up"):
        st.session_state.user_id = None
        st.session_state.logged_in = False
        st.experimental_rerun()

# Login/Sign-Up Page
def show_login_page():
    st.title("Login / Sign-Up")
    st.write("Please log in or sign up to continue.")
    
    user_name = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        # Find user by username
        user = next((u for u in data["profiles"] if u["name"] == user_name), None)
        if user:
            # Simple password check (In production, hash passwords!)
            if user.get("password") == password:
                st.session_state.user_id = user["id"]
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Incorrect password. Please try again.")
        else:
            st.error("User not found. Please sign up first.")
    
    if st.button("Sign Up"):
        if user_name and password:
            new_user_id = str(uuid.uuid4())
            new_user = {
                "id": new_user_id,
                "name": user_name,
                "password": password,
                "age": 18,  # Default age
                "interests": [],
                "bio": "",
            }
            data["profiles"].append(new_user)
            save_data(data)
            st.session_state.user_id = new_user_id
            st.session_state.logged_in = True
            st.success("Sign-up successful! You are now logged in.")
            st.experimental_rerun()
        else:
            st.error("Please fill in both fields.")

# Profile and Swiping Page
def show_main_page():
    st.title("Friendr 👋")
    user_id = st.session_state.user_id
    user_profile = next((p for p in data["profiles"] if p["id"] == user_id), None)
    
    if not user_profile:
        st.error("User profile not found. Please log out and sign up again.")
        return
    
    # Sidebar for editing profile
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
            st.session_state.logged_in = False
            st.experimental_rerun()

    # Main swiping area
    st.write("### Browse Profiles")
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
                    save_data(data)
                    st.session_state.current_index += 1
                    st.experimental_rerun()
            with col2:
                if st.button("👎 Skip", key=f"skip_{st.session_state.current_index}"):
                    st.session_state.current_index += 1
                    st.experimental_rerun()
        else:
            st.write("No more profiles to swipe!")
    else:
        st.write("No profiles available.")

# Routing logic
if st.session_state.logged_in:
    show_main_page()
elif st.session_state.user_id:
    show_login_page()
else:
    show_home_page()
