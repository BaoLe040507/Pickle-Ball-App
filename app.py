import streamlit as st
from auth_utils import sign_out, auth_screen
from utils import register_nav_pages

st.set_page_config(
    page_title="SmashTrack",
    layout="wide",
    initial_sidebar_state="auto"  # sidebar shown by default when logged in
)

def main_app(user_email: str):

    st.sidebar.button("Sign Out", on_click=sign_out)

    PAGE_DEFS = [
        {"page": "views/00_About.py",      "title": "About SmashTrack",   "icon": ":material/home:",        "default": True},
        {"page": "views/01_Profile.py",   "title": "Your Profile",     "icon": ":material/account_circle:"},
        {"page": "views/02_Match_Log.py",   "title": "Match History",      "icon": ":material/list_alt:"},
        {"page": "views/03_Dashboard.py",   "title": "Your Dashboard",     "icon": ":material/analytics:"},

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
