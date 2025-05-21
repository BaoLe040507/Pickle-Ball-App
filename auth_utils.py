from utils import get_supabase
import streamlit as st
import re


# ─── Auth Helpers ───────────────────────────────────────────────────────────────

def sign_up(email: str, password: str, display_name: str):
    """
    Pass `display_name` into Supabase as user metadata
    so it appears under auth.users.raw_user_meta_data ➞ display_name.
    """
    supabase = get_supabase()
    try:
        user = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"display_name": display_name}
            }
        })
        return user
    except Exception as e:
        st.error(f"Registration failed: {e}")


def sign_in(email: str, password: str):
    supabase = get_supabase()
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")


def sign_out():
    supabase = get_supabase()
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None
    except Exception as e:
        st.error(f"Logout failed: {e}")


# ─── Streamlit Auth Screen ────────────────────────────────────────────────────

def auth_screen():
    supabase = get_supabase()
    st.title("Authentication Page")
    option = st.selectbox("Choose an action:", ["Login", "Sign Up"], key="auth_option")

    email    = st.text_input("Email", key="auth_email")
    password = st.text_input("Password", type="password", key="auth_pwd")

    if option == "Sign Up":
        confirm      = st.text_input("Confirm Password", type="password", key="auth_confirm")
        display_name = st.text_input(
            "Display Name",
            key="auth_display_name",
            help="Letters and spaces only (e.g. John Doe)"
        )

        if st.button("Register"):
            # 1. validate locally
            if not email or not password or not confirm or not display_name:
                st.error("All fields are required.")
                return
            if password != confirm:
                st.error("Passwords do not match.")
                return
            if len(password) < 6:
                st.error("Password must be at least 6 characters.")
                return
            # allow letters and spaces only; no leading/trailing spaces
            display_name = display_name.strip()
            if not re.match(r"^[A-Za-z ]+$", display_name):
                st.error("Display Name may only contain letters and spaces.")
                return

            # 2. call sign_up with display_name
            user = sign_up(email, password, display_name)
            if hasattr(user, "error") and user.error:
                st.error(f"Registration failed: {user.error.message}")
            elif hasattr(user, "user") and user.user:
                st.success("Registration successful! Please check your email to confirm.")
                st.rerun()

    else:  # Login flow
        if st.button("Login"):
            if not email or not password:
                st.error("Enter both email and password.")
                return

            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if hasattr(user, "error") and user.error:
                st.error(f"Login failed: {user.error.message}")
            else:
                st.session_state.user_email = user.user.email
                st.rerun()