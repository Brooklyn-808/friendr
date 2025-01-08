import streamlit as st
import json
import os
import time

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
if "unseen_profiles" not in st.session_state:
    st.session_state.unseen_profiles = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "chat_with" not in st.session_state:
    st.session_state.chat_with = None
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

# Function to display a single profile card
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
            save_data(data)  # Save data after profile creation/edit
            st.sidebar.success("Profile saved!")
        else:
            st.sidebar.error("Please fill in all required fields!")

# Main app: Swipe functionality (Simulated with a swipeable animation)
if st.session_state.user_profile:
    st.write("### Browse Friends")
    profiles = [p for p in data["profiles"] if p["name"] != st.session_state.user_profile["name"]]

    # Update unseen_profiles list with new profiles
    unseen_names = {p["name"] for p in profiles}
    seen_names = {p["name"] for p in st.session_state.unseen_profiles}
    new_profiles = unseen_names - seen_names
    st.session_state.unseen_profiles += [p for p in profiles if p["name"] in new_profiles]

    # Check if someone liked the user
    user = st.session_state.user_profile["name"]
    liked_by_others = [u for u, liked_users in data["likes"].items() if user in liked_users]
    if liked_by_others:
        st.info(f"You've been liked by: {', '.join(liked_by_others)}")

    # Show the profiles as a slideshow
    if st.session_state.unseen_profiles:
        profile_names = [profile["name"] for profile in st.session_state.unseen_profiles]
        selected_profile_name = st.radio("Choose a profile to view", profile_names)

        # Get the profile that was selected
        selected_profile = next(profile for profile in st.session_state.unseen_profiles if profile["name"] == selected_profile_name)
        
        # Display the profile
        display_profile(selected_profile)

        # Swiping animation logic using HTML, CSS, and JavaScript
        swipe_script = """
        <style>
        .swipe-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px;
            transition: transform 0.5s ease;
        }
        .swipe-card {
            width: 300px;
            height: 400px;
            border-radius: 20px;
            background-color: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .dislike, .like {
            background-color: #f5f5f5;
            padding: 20px;
            border: none;
            cursor: pointer;
            border-radius: 10px;
            width: 100px;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .dislike:hover {
            background-color: #ff4d4d;
            color: white;
        }
        .like:hover {
            background-color: #4CAF50;
            color: white;
        }
        </style>
        <div class="swipe-container">
            <div class="swipe-card">
                <h3>{}</h3>
                <p>Age: {}</p>
                <p>Interests: {}</p>
                <p>Bio: {}</p>
            </div>
        </div>
        <div style="display: flex; justify-content: center;">
            <button class="dislike">👎 Dislike</button>
            <button class="like">👍 Like</button>
        </div>
        """.format(selected_profile["name"], selected_profile["age"], ", ".join(selected_profile["interests"]), selected_profile["bio"])

        st.markdown(swipe_script, unsafe_allow_html=True)

        # Button for swiping left or right (simulate swipe)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👎 Dislike"):
                # Simulate swipe left (dislike)
                st.session_state.unseen_profiles.remove(selected_profile)
                save_data(data)
        with col2:
            if st.button("👍 Like"):
                # Simulate swipe right (like)
                if user not in data["likes"]:
                    data["likes"][user] = []
                data["likes"][user].append(selected_profile["name"])
                st.session_state.unseen_profiles.remove(selected_profile)
                save_data(data)  # Save data after liking a profile

        st.session_state.current_index += 1
    else:
        st.write("No more profiles to swipe! 😔")
        if st.button("🔄 Refresh Profiles"):
            # Cooldown: Allow refresh only if 5 seconds have passed since the last refresh
            current_time = time.time()
            if current_time - st.session_state.last_refresh >= 5:
                st.session_state.last_refresh = current_time
                st.session_state.current_index = 0
                st.session_state.unseen_profiles = [p for p in profiles if p["name"] not in seen_names]
                st.success("Profiles refreshed! 🎉")
            else:
                st.warning("Please wait 5 seconds before refreshing again.")

    # Check if there's a mutual like to start chat
    if user in data["likes"]:
        mutual_matches = [u for u in data["likes"][user] if user in data["likes"].get(u, [])]
        if mutual_matches:
            st.write("### Mutual Matches")
            for match in mutual_matches:
                if st.button(f"Chat with {match}"):
                    st.session_state.chat_with = match

    # Handle the chat functionality
    if st.session_state.chat_with:
        st.write(f"### Chat with {st.session_state.chat_with}")
        chat_key = f"{user}_to_{st.session_state.chat_with}"
        if chat_key not in data["messages"]:
            data["messages"][chat_key] = []
        messages = data["messages"][chat_key]
        for msg in messages:
            st.write(msg)

        message_input = st.text_input("Your message:", key="message_input")
        if st.button("Send Message") and message_input:
            data["messages"][chat_key].append(f"{user}: {message_input}")
            save_data(data)  # Save message
            st.session_state.chat_with = None  # Close the chat after sending the message
            st.experimental_rerun()  # Refresh the page

