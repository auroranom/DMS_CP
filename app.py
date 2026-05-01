import streamlit as st
from db import login_user
from utils.session_utils import initialize_session, login_user as set_session

st.set_page_config(page_title="NutChoc ERP - Login", page_icon="🍫", layout="centered")
initialize_session()

if not st.session_state.logged_in:
    st.title("🍫 NutChoc ERP")
    st.caption("Production & Inventory Management System")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login", use_container_width=True):
            user = login_user(username, password)
            if user:
                set_session(user)
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.divider()
    st.caption("Manager: manager1 / manager123")

else:
    if st.session_state.role == "manager":
        st.switch_page("pages/manager_dashboard.py")
    elif st.session_state.role == "supplier":
        st.switch_page("pages/supplier_dashboard.py")