from supabase import Client, AuthApiError
from utils import get_supabase
import streamlit as st


# ─── Auth Helpers ───────────────────────────────────────────────────────────────

def sign_up(email: str, password: str):
    """Try to register a new user. Returns dict with 'user' or 'error'."""
    supabase: Client = get_supabase()
    try:
        resp = supabase.auth.sign_up({"email": email, "password": password})
        user = resp.user
        return {
            "user": {
                "id": user.id,
                "email": user.email,
            }
        }
    except AuthApiError as err:
        return {"error": err.message}
    except Exception as err:
        return {"error": str(err)}


def sign_in(email: str, password: str):
    """Try to sign in. Returns dict with 'user' or 'error'."""
    supabase: Client = get_supabase()
    try:
        resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = resp.user
        return {
            "user": {
                "id": user.id,
                "email": user.email,
            }
        }
    except AuthApiError as err:
        return {"error": err.message}
    except Exception as err:
        return {"error": str(err)}


def sign_out():
    """Clear the session key; don't call rerun here."""
    supabase = get_supabase()
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None

    except Exception as err:
        st.error(f"Logout failed: {err}")
    st.session_state.user_email = None


# ─── Streamlit Auth Screen ────────────────────────────────────────────────────

def auth_screen():

    # ensure our session key is defined
    if "user_email" not in st.session_state:
        st.session_state.user_email = None

    st.title("Authentication")

    option = st.selectbox(
        "Action",
        ["Login", "Sign Up"],
        key="auth_option"
    )

    if option == "Sign Up":
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            pwd1  = st.text_input("Password", type="password", key="signup_pwd1")
            pwd2  = st.text_input("Confirm Password", type="password", key="signup_pwd2")
            submitted = st.form_submit_button("Register")

            if submitted:
                if not (email and pwd1 and pwd2):
                    st.error("All fields required.")
                    return
                if pwd1 != pwd2:
                    st.error("Passwords must match.")
                    return

                resp = sign_up(email, pwd1)
                if resp.get("error"):
                    st.error(resp["error"])
                else:
                    st.success("Registered! Check your email to confirm.")
                    st.rerun()

    else:  # Login flow
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            pwd   = st.text_input("Password", type="password", key="login_pwd")
            submitted = st.form_submit_button("Login")

            if submitted:
                if not (email and pwd):
                    st.error("Enter both fields.")
                    return

                resp = sign_in(email, pwd)
                if resp.get("error"):
                    st.error(resp["error"])
                elif resp.get("user") and "email" in resp["user"]:
                    st.session_state.user_email = resp["user"]["email"]
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error("Unexpected login response. Please try again.")
