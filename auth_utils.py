from utils import get_supabase, clear_user_cache
import streamlit as st
import re
from streamlit_cookies_manager import EncryptedCookieManager

# ─── Cookie Manager Setup ──────────────────────────────────────────────────────

cookies = EncryptedCookieManager(
    prefix="pickleball_",
    password=st.secrets["cookies"]["password"]
)
if not cookies.ready():
    st.stop()

def save_session_to_cookie(session):
    if session and hasattr(session, "access_token") and hasattr(session, "refresh_token"):
        cookies["access_token"] = session.access_token
        cookies["refresh_token"] = session.refresh_token
        cookies.save()

def restore_session_from_cookie():
    access_token = cookies.get("access_token")
    refresh_token = cookies.get("refresh_token")
    if access_token and refresh_token:
        supabase = get_supabase()
        try:
            user_response = supabase.auth.get_user(access_token)
            if user_response and user_response.user:
                # Only set session state if we successfully get user data
                st.session_state["user"] = user_response.user
                st.session_state["user_email"] = user_response.user.email
                return True
        except Exception as e:
            # Clear invalid session data
            clear_session_state()
            clear_cookies()
    return False

def clear_session_state():
    """Clear all user-related session state"""
    keys_to_clear = ["user", "user_email", "supabase_session"]
    for key in keys_to_clear:
        st.session_state.pop(key, None)

def clear_cookies():
    """Clear authentication cookies"""
    cookies["access_token"] = ""
    cookies["refresh_token"] = ""
    cookies.save()

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
        # Clear any existing session state first
        clear_session_state()
        clear_user_cache()
        
        # Optionally auto-login after sign up if no error and user returned
        if hasattr(res, "user") and res.user:
            st.session_state["user"] = res.user
            st.session_state["user_email"] = res.user.email
        if hasattr(res, "session") and res.session:
            st.session_state["supabase_session"] = res.session
            save_session_to_cookie(res.session)
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
        
        # Clear any existing session state first
        clear_session_state()
        clear_user_cache()
        
        # On success, store session and user for later rehydration
        if hasattr(res, "session") and res.session:
            st.session_state["supabase_session"] = res.session
            save_session_to_cookie(res.session)
        if hasattr(res, "user") and res.user:
            st.session_state["user"] = res.user
            st.session_state["user_email"] = res.user.email
        return res
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    """Sign out and clear all session data"""
    supabase = get_supabase()
    try:
        supabase.auth.sign_out()
    except Exception as e:
        st.error(f"Logout failed: {e}")
    finally:
        # Always clear session state and cache, even if sign_out fails
        clear_session_state()
        clear_cookies()
        clear_user_cache()

# ─── Streamlit Auth Screen ────────────────────────────────────────────────────

def auth_screen():
    # Only try to restore session if user is not already logged in
    if not st.session_state.get("user_email"):
        restore_session_from_cookie()

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