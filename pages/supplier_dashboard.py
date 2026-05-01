"""
Supplier Dashboard
Nut Chocolate Production & Inventory Management System
"""

import streamlit as st
import pandas as pd
from datetime import date
import db
from utils.session_utils import initialize_session, logout_user

# Security Check 
initialize_session()

if not st.session_state.logged_in:
    st.warning("Please login first")
    st.stop()

if st.session_state.role != "supplier":
    st.error("Access denied. Supplier only.")
    st.stop()

# Page config 
st.set_page_config(page_title="Supplier Portal", page_icon="📦", layout="wide")

#  Global CSS (matches manager dark theme) 
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    }
    [data-testid="stSidebar"] * { color: #f0f0f0 !important; }
    [data-testid="stSidebar"] .stRadio label { color: #ffffff !important; font-weight: 500; }
    [data-testid="stSidebar"] .stCaption { color: #c0c8d8 !important; }

    /* Main background */
    .stApp { background: #0d1117; color: #e6edf3; }

    /* All body text clearly visible */
    p, span, div, li, td, th { color: #e6edf3; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #f0883e, #d45f00);
        color: #ffffff !important; border: none; border-radius: 8px;
        padding: 0.5rem 1.4rem; font-weight: 700;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(240,136,62,0.4);
    }

    /* Section headers */
    h1 { color: #f0883e !important; font-weight: 800; }
    h2, h3 { color: #ffffff !important; font-weight: 700; }
    h4, h5, h6 { color: #e6edf3 !important; font-weight: 600; }

    /* Inputs — bright labels */
    .stTextInput input, .stNumberInput input, .stSelectbox select,
    .stDateInput input, .stTextArea textarea {
        background: #161b22 !important; color: #ffffff !important;
        border: 1px solid #58a6ff !important; border-radius: 8px !important;
        font-size: 0.95rem !important;
    }
    label, .stSelectbox label, .stTextInput label,
    .stNumberInput label, .stDateInput label, .stTextArea label,
    .stRadio label, .stCheckbox label {
        color: #c9d1d9 !important; font-weight: 600 !important; font-size: 0.88rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] { color: #c9d1d9 !important; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #f0883e !important; border-bottom: 2px solid #f0883e; }

    /* Dataframe / table */
    .stDataFrame, [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
    .stDataFrame tbody tr td { color: #e6edf3 !important; }
    .stDataFrame thead tr th { color: #f0883e !important; font-weight: 700 !important; }

    /* Captions */
    .stCaption, [data-testid="stCaptionContainer"] { color: #c9d1d9 !important; }

    /* Info / success / warning / error banners */
    [data-testid="stAlert"] { border-radius: 10px; }
    .stSuccess { background: #1b3a2a; border-left: 4px solid #3fb950; color: #d1ffd9 !important; }
    .stWarning { background: #3a2800; border-left: 4px solid #f0883e; color: #ffe8c0 !important; }
    .stInfo    { background: #0d2137; border-left: 4px solid #58a6ff; color: #cce8ff !important; }
    .stError   { background: #3a0e0e; border-left: 4px solid #f85149; color: #ffd0ce !important; }

    /* Divider */
    hr { border-color: #30363d; }

    /* Page title banner */
    .page-banner {
        background: linear-gradient(135deg, #161b22, #0f3460);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 20px 28px;
        margin-bottom: 24px;
    }
    .page-banner h1 { margin: 0; font-size: 1.8rem; }
    .page-banner p  { margin: 4px 0 0; color: #c9d1d9 !important; font-size: 0.95rem; font-weight: 500; }

    /* Status badge helper */
    .badge-approved { color: #3fb950; font-weight: 700; }
    .badge-rejected { color: #f85149; font-weight: 700; }
    .badge-pending  { color: #f0883e; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

#  Get supplier_id from session 
supplier_id = st.session_state.get("supplier_id", None)

# Sidebar 
with st.sidebar:
    st.markdown("## 📦 **Supplier Portal**")
    st.markdown(f"*Welcome, **{st.session_state.username}***")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["📋 My Orders", "➕ Submit Supply", "📜 History", "🔔 Notifications"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Nut Chocolate Manufacturing Unit")
    st.caption("DBMS Course Project – 2026")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.switch_page("app.py")


#  PAGE 1 – MY ORDERS
if page == "📋 My Orders":
    st.markdown(
        """<div class='page-banner'>
            <h1>📋 My Orders</h1>
            <p>Supply requests submitted <strong>today</strong></p>
        </div>""",
        unsafe_allow_html=True,
    )

    if supplier_id:
        requests = db.get_supplier_requests_today(supplier_id)
        if requests:
            df = pd.DataFrame(requests)
            df.columns = ["_id", "Item", "Quantity", "Unit", "Date", "Notes", "Status", "Submitted"]
            df.insert(0, "S.No", range(1, len(df) + 1))
            st.dataframe(df.drop(columns=["_id"]), hide_index=True, use_container_width=True)
        else:
            st.info("🗓️ No orders submitted today. Use ‘Submit Supply’ to place a new request!")

        # --- Editable Pending Requests ---
        pending = db.get_pending_supplier_requests(supplier_id)
        if pending:
            st.markdown("---")
            st.subheader("✏️ Edit Pending Requests")
            st.caption("You can modify requests until the manager approves or rejects them.")

            for idx, req in enumerate(pending, start=1):
                with st.expander(f"📝 #{idx}: {req['item_name']} — {req['quantity']} {req['unit']}"):
                    with st.form(f"edit_req_{req['id']}", clear_on_submit=False):
                        col1, col2 = st.columns(2)
                        edit_item = col1.text_input("Item Name", value=req["item_name"], key=f"ei_{req['id']}")
                        edit_qty = col2.number_input("Quantity", min_value=1, value=int(req["quantity"]), step=1, key=f"eq_{req['id']}")
                        col3, col4 = st.columns(2)
                        unit_options = ["kg", "g", "litre", "pcs"]
                        unit_idx = unit_options.index(req["unit"]) if req["unit"] in unit_options else 0
                        edit_unit = col3.selectbox("Unit", unit_options, index=unit_idx, key=f"eu_{req['id']}")
                        edit_date = col4.date_input("Supply Date",
                                                     value=req["supply_date"] if req["supply_date"] else date.today(),
                                                     key=f"ed_{req['id']}")
                        edit_notes = st.text_area("Notes", value=req["notes"] or "", key=f"en_{req['id']}")

                        if st.form_submit_button("💾 Save Changes", use_container_width=True):
                            if edit_item.strip():
                                db.update_supply_request(req["id"], edit_item.strip(), edit_qty, edit_unit, edit_date, edit_notes)
                                st.success(f"✅ Request #{req['id']} updated!")
                                st.rerun()
                            else:
                                st.error("❌ Item name cannot be empty.")
    else:
        st.warning("⚠️ Supplier profile not linked. Contact admin.")


#  PAGE 2 – SUBMIT SUPPLY
elif page == "➕ Submit Supply":
    st.markdown(
        """<div class='page-banner'>
            <h1>➕ Submit Supply Request</h1>
            <p>Request raw materials or packaging to be delivered</p>
        </div>""",
        unsafe_allow_html=True,
    )

    with st.form("supply_form", clear_on_submit=True):
        item_name = st.text_input("Item Name *", placeholder="e.g., Cocoa Powder")

        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity *", min_value=1, step=1)
        with col2:
            unit = st.selectbox("Unit", ["kg", "g", "litre", "pcs"])

        supply_date = st.date_input("Supply Date", value=date.today())
        notes = st.text_area("Notes (optional)", placeholder="Any special instructions…")

        if st.form_submit_button("📤 Submit Request", use_container_width=True):
            if item_name and quantity > 0 and supplier_id:
                db.add_supply_request(supplier_id, item_name, quantity, unit, supply_date, notes)
                st.success(f"✅ Request submitted for **{quantity} {unit}** of **{item_name}**")
                st.rerun()
            elif not supplier_id:
                st.error("❌ Supplier profile not linked. Contact admin.")
            else:
                st.error("❌ Please fill in the item name and quantity.")


# ════════════════════════════════════════════════════════════
#  PAGE 3 – HISTORY
# ════════════════════════════════════════════════════════════
elif page == "📜 History":
    st.markdown(
        """<div class='page-banner'>
            <h1>📜 Submission History</h1>
            <p>Complete log of <strong>all</strong> your past and present supply requests</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if supplier_id:
        requests = db.get_supplier_requests(supplier_id)
        if requests:
            df = pd.DataFrame(requests)
            df.columns = ["_id", "Item", "Quantity", "Unit", "Date", "Notes", "Status", "Submitted"]
            df.insert(0, "S.No", range(1, len(df) + 1))
            display_df = df.drop(columns=["_id"])
            # Highlight today's rows
            today_str = str(date.today())
            def highlight_today(row):
                submitted = str(row["Submitted"])[:10]
                color = "#1b2a1b" if submitted == today_str else ""
                return [f"background-color: {color}"] * len(row)
            styled = display_df.style.apply(highlight_today, axis=1)
            st.dataframe(styled, hide_index=True, use_container_width=True)
            st.caption("🟢 Green rows = submitted today")
        else:
            st.info("No history yet. Start by submitting a supply request!")
    else:
        st.warning("⚠️ Supplier profile not linked. Contact admin.")


# ════════════════════════════════════════════════════════════
#  PAGE 4 – NOTIFICATIONS
# ════════════════════════════════════════════════════════════
elif page == "🔔 Notifications":
    st.markdown(
        """<div class='page-banner'>
            <h1>🔔 Notifications</h1>
            <p>Status updates on your submitted requests</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if supplier_id:
        requests = db.get_supplier_requests(supplier_id)
        if requests:
            for r in requests:
                status = r["status"]
                if status == "Approved":
                    st.success(f"✅ **{r['item_name']}** — {r['quantity']} {r['unit']} | **Approved**")
                elif status == "Rejected":
                    st.error(f"❌ **{r['item_name']}** — {r['quantity']} {r['unit']} | **Rejected**")
                else:
                    st.info(f"⏳ **{r['item_name']}** — {r['quantity']} {r['unit']} | **Pending Review**")
                st.caption(f"Submitted: {r['created_at']}")
                st.divider()
        else:
            st.info("🔕 No notifications yet.")
    else:
        st.warning("⚠️ Supplier profile not linked. Contact admin.")