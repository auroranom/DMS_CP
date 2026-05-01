import streamlit as st

def initialize_session():
    """Initialize session state keys independently so a partial state
    (e.g. after hot-reload) never leaves supplier_id undefined."""
    defaults = {
        "logged_in": False,
        "user_id": None,
        "username": None,
        "role": None,
        "supplier_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def login_user(user):
    st.session_state.logged_in = True
    st.session_state.user_id = user["id"]
    st.session_state.username = user["username"]
    st.session_state.role = user["role"]
    st.session_state.supplier_id = user.get("supplier_id", None)

def logout_user():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.supplier_id = None