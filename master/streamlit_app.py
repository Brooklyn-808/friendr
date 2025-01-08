import streamlit as st

# App title
st.title("Friendr 👋")
st.subheader("Find your next best friend!")

# Fake database for user profiles
profiles = [
    {"name": "Alice", "age": 25, "interests": ["Hiking", "Music", "Art"], "bio": "Lover of all things nature."},
    {"name": "Bob", "age": 28, "interests": ["Gaming", "Tech", "Cooking"], "bio": "Always up for a co-op game or a cooking session!"},
    {"name": "Charlie", "age": 23, "interests": ["Reading", "Travel", "Photography"], "bio": "Capturing moments one photo at a time."},
]

# User profile input
st.sidebar.title("Create Your Profile")
user_name = st.sidebar.text_input("Your Name", "")
user_age = st.sidebar.number_input("Your Age", min_value=13, max_value=100, value=18)
user_interests = st.sidebar.text_input("Your Interests (comma-separated)", "")
user_bio = st.sidebar.text_area("Your Bio", "")

# Save user profile
if st.sidebar.button("Save Profile"):
    if user_name and user_interests:
        profiles.append({
            "name": user_name,
            "age": user_age,
            "interests": [i.strip() for i in user_interests.split(",")],
            "bio": user_bio,
        })
        st.sidebar.success("Profile saved! You can now browse friends.")
    else:
        st.sidebar.error("Please fill in your name and interests!")

# Display user profiles
st.write("### Browse Friends")
if len(profiles) > 0:
    for profile in profiles:
        st.write(f"**{profile['name']}** ({profile['age']} years old)")
        st.write(f"**Interests:** {', '.join(profile['interests'])}")
        st.write(f"**Bio:** {profile['bio']}")
        if st.button(f"Send Friend Request to {profile['name']}"):
            st.success(f"Friend request sent to {profile['name']}!")
        st.divider()
else:
    st.write("No profiles found! Create your profile to get started.")

