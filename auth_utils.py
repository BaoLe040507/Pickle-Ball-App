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
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"display_name": display_name}
            }
        })
        # Optionally auto-login after sign up if no error and user returned
        if hasattr(res, "user") and res.user:
            st.session_state["user"] = res.user
            st.session_state["user_email"] = res.user.email
        return res
    except Exception as e:
        st.error(f"Registration failed: {e}")

def sign_in(email: str, password: str):
    """
    Sign in with email/password, then persist session & user in Streamlit state
    so the login survives page refreshes.
    """
    supabase = get_supabase()
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        # On success, store session and user for later rehydration
        if hasattr(res, "session") and res.session:
            st.session_state["supabase_session"] = res.session
        if hasattr(res, "user") and res.user:
            st.session_state["user"] = res.user
            st.session_state["user_email"] = res.user.email
        return res
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    supabase = get_supabase()
    try:
        supabase.auth.sign_out()
        # Clear stored session & user
        st.session_state.pop("supabase_session", None)
        st.session_state.pop("user", None)
        st.session_state.pop("user_email", None)
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
            display_name = display_name.strip()
            if not re.match(r"^[A-Za-z ]+$", display_name):
                st.error("Display Name may only contain letters and spaces.")
                return

            # 2. call sign_up with display_name
            res = sign_up(email, password, display_name)
            if hasattr(res, "error") and res.error:
                st.error(f"Registration failed: {res.error.message}")
            else:
                st.success("Registration successful! Please check your email to confirm.")
                st.rerun()

    else:  # Login flow
        if st.button("Login"):
            if not email or not password:
                st.error("Enter both email and password.")
                return

            res = sign_in(email, password)
            if hasattr(res, "error") and res.error:
                st.error(f"Login failed: {res.error.message}")
            else:
                st.success("Login successful!")
                st.rerun()