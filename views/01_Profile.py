import streamlit as st
from utils import get_supabase, getCurrentLevel,set_player_level

def profile_page():
    supabase = get_supabase()
    st.title("Profile Page")
    st.divider()

    # get_user() returns a UserResponse with a `.user` attribute
    resp = supabase.auth.get_user()
    user = resp.user  
    if user:
        # user_metadata is where we stored display_name
        display_name = user.user_metadata.get("display_name", "Unknown User")
    else:
        display_name = "Unknown User"

    st.markdown(f"Welcome, {display_name}!")

    col1, col2 = st.columns([1,2], border= True)
    with col1:
        st.subheader("Your Profile")
        st.markdown(f"**Email:** {user.email}")
    
    with col2:
        st.subheader("Your Current Level")
        st.markdown(getCurrentLevel(user.id))
        with st.expander("Update Level"):
            new_level = st.selectbox(
                "Select New Level",
                ["2.0","2.5","3.0","3.5","4.0","4.5","5.0"],
                key="new_level"
            )
            effective_date = st.date_input(
                "Effective Date",
                key="effective_date"
            )
            notes = st.text_area(
                "Notes",
                key="notes"
            )

        if st.button("Submit", key="submit_level"):
            set_player_level(user.id, new_level, effective_date, notes)
            st.success("Level updated successfully!")


if __name__ == "__main__":
    profile_page()