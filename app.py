import streamlit as st
from auth_utils import sign_out, auth_screen
from utils import register_nav_pages

def main_app(user_email: str):

    if st.sidebar.button("Sign Out"):
        sign_out()
        st.markdown("You have been signed out.")

    PAGE_DEFS = [
        {"page": "views/About.py",      "title": "About SmashTrack",   "icon": ":material/home:",        "default": True},
        {"page": "views/Match_Log.py",   "title": "Match History",      "icon": ":material/list_alt:"},
        {"page": "views/Dashboard.py",   "title": "Your Dashboard",     "icon": ":material/analytics:"}
    ]
    pages = register_nav_pages(PAGE_DEFS)
    pg = st.navigation(pages=pages)

    st.logo("assets/logo.png", size="large")

    st.sidebar.text("Made by Bao Le")

    pg.run()


# entrypoint
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if st.session_state.user_email:
    main_app(st.session_state.user_email)
else:

    auth_screen()
