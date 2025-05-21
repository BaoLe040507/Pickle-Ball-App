import streamlit as st
from utils import get_supabase, getCurrentLevel,set_player_level

def profile_page():
    supabase = get_supabase()
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("assets/user.png", width=100)
    with col2:
        st.title("Profile Page")

    st.divider()

    st.markdown("""
       **The SmashTrack Profile Page** is where you can view and update your profile information, including your current level.
    """)   

    # get_user() returns a UserResponse with a `.user` attribute
    resp = supabase.auth.get_user()
    user = resp.user  
    if user:
        # user_metadata is where we stored display_name
        display_name = user.user_metadata.get("display_name", "Unknown User")
    else:
        display_name = "Unknown User"

    st.markdown(f"""Welcome, :green-background[**{display_name}**] !""")

    col1, col2 = st.columns([1,2], border= True)
    with col1:
        st.subheader("📧 Your Profile")
        st.markdown(f"**Email:** {user.email}")
    
    with col2:
        st.subheader("💪 Your Current Level")
        current_level = getCurrentLevel(user.id)
        st.markdown(f""" Your Current Level: :blue-background[**{current_level}**]""")

        if "show_level_form" not in st.session_state:
            st.session_state.show_level_form = False

        if st.button("Update Level", key="toggle_form"):
            st.session_state.show_level_form = not st.session_state.show_level_form

        # Show the form if toggled on
        if st.session_state.show_level_form:
            new_level      = st.selectbox("Select New Level", ["2.0","2.5","3.0","3.5","4.0","4.5","5.0", "5.5"])
            effective_date = st.date_input("Effective Date")
            notes          = st.text_area("Notes")

            if st.button("Submit", key="submit_form"):
                resp = set_player_level(user.id, new_level, effective_date, notes)
                if resp.data:
                    # Invalidate cache so next getCurrentLevel() is fresh
                    getCurrentLevel.clear()
                    st.success("Level updated!")
                    # Rerun the script to immediately show the new level
                    st.rerun()
                else:
                    st.error("Failed to update level")


if __name__ == "__main__":
    profile_page()