"""
NutChoc ERP - Manager Dashboard
Production & Inventory Management System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import db

#  Security Check 
from utils.session_utils import initialize_session, logout_user

initialize_session()

if not st.session_state.logged_in:
    st.warning("Please login first")
    st.stop()

if st.session_state.role != "manager":
    st.error("Access denied. Manager only.")
    st.stop()

#  Page config 
st.set_page_config(
    page_title="NutChoc ERP",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS 
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

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #161b22, #21262d);
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 18px 22px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    }
    [data-testid="metric-container"] label { color: #c9d1d9 !important; font-size: 0.82rem; font-weight: 600; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f0883e !important; font-size: 2rem !important; font-weight: 800;
    }

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
    </style>
    """,
    unsafe_allow_html=True,
)

#  Sidebar navigation 
with st.sidebar:
    st.markdown("## 🍫 **NutChoc ERP**")
    st.markdown("*Production & Inventory System*")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            "🏠  Dashboard",
            "🏭  Supplier Management",
            "🥄  Raw Material Management",
            "⚙️  Production Batches",
            "📦  Inventory Monitoring",
            "📊  Reports",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Nut Chocolate Manufacturing Unit")
    st.caption("DBMS Course Project – 2026")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.switch_page("app.py")


#  PAGE 1 – DASHBOARD
if page == "🏠  Dashboard":
    st.markdown(
        """<div class='page-banner'>
            <h1>🏠 Dashboard</h1>
            <p>Real-time overview of your chocolate manufacturing unit</p>
        </div>""",
        unsafe_allow_html=True,
    )

    stats = db.get_dashboard_stats()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("🏭 Suppliers",        stats["total_suppliers"])
    c2.metric("🥄 Raw Materials",    stats["total_materials"])
    c3.metric("⚙️ Total Batches",    stats["total_batches"])
    c4.metric("🍫 Grand Total",       f"{stats['grand_total_produced']:,}")
    st.divider()
    
    # 🆕 Pending Supply Requests
    st.subheader("⏳ Pending Supply Requests")
    pending = db.get_pending_requests()
    
    if pending:
        for req in pending:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
            with col1:
                st.write(f"**{req['supplier_name']}**")
            with col2:
                st.write(f"{req['item_name']} ({req['quantity']} {req['unit']})")
            with col3:
                st.write(req['supply_date'])
            with col4:
                st.write(req['created_at'].strftime('%Y-%m-%d') if req['created_at'] else '')
            with col5:
                if st.button("✅ Approve", key=f"approve_{req['id']}"):
                    db.update_request_status(req['id'], 'Approved')
                    st.success("Approved!")
                    st.rerun()
            with col6:
                if st.button("❌ Reject", key=f"reject_{req['id']}"):
                    db.update_request_status(req['id'], 'Rejected')
                    st.error("Rejected!")
                    st.rerun()
            st.divider()
    else:
        st.info("No pending requests.")
    c5.metric("📅 Today's Output",   f"{stats['today_produced']:,}")
    c6.metric("⚠️ Low-Stock Items",  stats["low_stock_count"],
              delta_color="inverse" if stats["low_stock_count"] > 0 else "off")

    st.markdown("---")
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.subheader("📈 Daily Production Chart")
        chart_data = db.get_daily_production_chart_data()
        if chart_data:
            df_chart = pd.DataFrame(chart_data)
            df_chart["total"] = df_chart["total"].astype(int)
            fig = px.bar(
                df_chart,
                x="date", y="total",
                text="total",
                color_discrete_sequence=["#f0883e"],
                template="plotly_dark",
                labels={"date": "Production Date", "total": "Chocolates Produced"},
            )
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(
                plot_bgcolor="#161b22",
                paper_bgcolor="#161b22",
                font=dict(color="#e6edf3"),
                showlegend=False,
                xaxis=dict(gridcolor="#30363d"),
                yaxis=dict(gridcolor="#30363d"),
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No production data yet. Record your first batch!")

    with col_r:
        st.subheader("⚠️ Low Stock Alerts")
        low = db.get_low_stock_materials()
        if low:
            for item in low:
                pct = (float(item["quantity"]) / float(item["reorder_level"]) * 100
                       if float(item["reorder_level"]) > 0 else 0)
                st.warning(
                    f"**{item['name']}** — {item['quantity']} "
                    f"(reorder at {item['reorder_level']})"
                )
        else:
            st.success("✅ All materials adequately stocked!")

        st.markdown("---")
        st.subheader("📋 Recent Batches")
        batches = db.get_all_batches()
        if batches:
            recent = batches[:6]
            for b in recent:
                st.markdown(
                    f"📅 **{b['production_date']}** — "
                    f"Batch {b['batch_number']}: **{b['quantity_produced']:,}** pcs"
                )
        else:
            st.info("No batches recorded yet.")


#  PAGE 2 – SUPPLIER MANAGEMENT
elif page == "🏭  Supplier Management":
    st.markdown(
        """<div class='page-banner'>
            <h1>🏭 Supplier Management</h1>
            <p>Add, update, and manage your raw material suppliers</p>
        </div>""",
        unsafe_allow_html=True,
    )

    tab_view, tab_add, tab_edit = st.tabs(["📋 All Suppliers", "➕ Add Supplier", "✏️ Edit / Delete"])

    with tab_view:
        suppliers = db.get_all_suppliers()
        if suppliers:
            df = pd.DataFrame(suppliers)
            df.columns = ["ID", "Name", "Phone", "Email", "Address"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No suppliers found. Add one using the tab above.")

    with tab_add:
        st.subheader("Add New Supplier")
        with st.form("add_supplier_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name    = col1.text_input("Supplier Name *")
            phone   = col2.text_input("Contact Phone")
            email   = col1.text_input("Email Address")
            address = col2.text_input("Address")
            submitted = st.form_submit_button("➕ Add Supplier")
            if submitted:
                if not name.strip():
                    st.error("Supplier name is required.")
                else:
                    db.add_supplier(name.strip(), phone, email, address)
                    st.success(f"✅ Supplier **{name}** added successfully!")
                    st.rerun()

    with tab_edit:
        suppliers = db.get_all_suppliers()
        if not suppliers:
            st.info("No suppliers to edit.")
        else:
            options = {f"{s['name']} (ID: {s['supplier_id']})": s for s in suppliers}
            choice = st.selectbox("Select Supplier", list(options.keys()))
            s = options[choice]

            with st.form("edit_supplier_form"):
                col1, col2 = st.columns(2)
                name    = col1.text_input("Name",    value=s["name"])
                phone   = col2.text_input("Phone",   value=s["contact_phone"] or "")
                email   = col1.text_input("Email",   value=s["email"] or "")
                address = col2.text_input("Address", value=s["address"] or "")
                c_save, c_del = st.columns(2)
                save = c_save.form_submit_button("💾 Save Changes")
                delete = c_del.form_submit_button("🗑️ Delete Supplier", type="secondary")

            if save:
                db.update_supplier(s["supplier_id"], name, phone, email, address)
                st.success("✅ Supplier updated!")
                st.rerun()
            if delete:
                db.delete_supplier(s["supplier_id"])
                st.success("✅ Supplier deleted.")
                st.rerun()


#  PAGE 3 – RAW MATERIAL MANAGEMENT
elif page == "🥄  Raw Material Management":
    st.markdown(
        """<div class='page-banner'>
            <h1>🥄 Raw Material Management</h1>
            <p>Track ingredient and packaging stock levels</p>
        </div>""",
        unsafe_allow_html=True,
    )

    tab_view, tab_add, tab_stock, tab_del, tab_recipe = st.tabs(
        ["📋 All Materials", "➕ Add Material", "🔄 Update Stock", "🗑️ Delete", "🧪 Recipe"]
    )

    with tab_view:
        materials = db.get_all_raw_materials()
        if materials:
            df = pd.DataFrame(materials)
            display_cols = ["material_id", "name", "unit", "quantity", "reorder_level", "supplier_name"]
            df = df[display_cols]
            df.columns = ["ID", "Material Name", "Unit", "In Stock", "Reorder Level", "Supplier"]

            def highlight_low(row):
                color = "#3a1a00" if float(row["In Stock"]) <= float(row["Reorder Level"]) else ""
                return [f"background-color: {color}"] * len(row)

            styled = df.style.apply(highlight_low, axis=1)
            st.dataframe(styled, use_container_width=True, hide_index=True)
            st.caption("🟠 Highlighted rows have stock at or below reorder level.")
        else:
            st.info("No raw materials found.")

    with tab_add:
        st.subheader("Add New Raw Material")
        suppliers = db.get_all_suppliers()
        supplier_opts = {"None": None}
        supplier_opts.update({s["name"]: s["supplier_id"] for s in suppliers})
        with st.form("add_rm_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name     = col1.text_input("Material Name *")
            unit     = col2.selectbox("Unit", ["kg", "g", "litre", "ml", "pcs", "metres"])
            qty      = col1.number_input("Initial Quantity", min_value=0.0, step=0.5)
            reorder  = col2.number_input("Reorder Level",   min_value=0.0, step=0.5)
            supplier = st.selectbox("Supplier", list(supplier_opts.keys()))
            submitted = st.form_submit_button("➕ Add Material")
            if submitted:
                if not name.strip():
                    st.error("Material name is required.")
                else:
                    db.add_raw_material(name.strip(), unit, qty, reorder, supplier_opts[supplier])
                    st.success(f"✅ **{name}** added!")
                    st.rerun()

    with tab_stock:
        st.subheader("Update Stock Quantity")
        materials = db.get_all_raw_materials()
        if not materials:
            st.info("No materials to update.")
        else:
            opts = {f"{m['name']} ({m['unit']}) — stock: {m['quantity']}": m for m in materials}
            choice = st.selectbox("Select Material", list(opts.keys()))
            m = opts[choice]
            new_qty = st.number_input(
                "New Quantity", min_value=0.0, value=float(m["quantity"]), step=0.5
            )
            if st.button("🔄 Update Stock"):
                db.update_raw_material_stock(m["material_id"], new_qty)
                st.success(f"✅ Stock updated to {new_qty} {m['unit']}")
                st.rerun()

    with tab_del:
        st.subheader("Delete Raw Material")
        materials = db.get_all_raw_materials()
        if not materials:
            st.info("No materials to delete.")
        else:
            opts = {f"{m['name']} (ID: {m['material_id']})": m for m in materials}
            choice = st.selectbox("Select Material to Delete", list(opts.keys()))
            m = opts[choice]
            st.warning(f"⚠️ This will permanently delete **{m['name']}**.")
            if st.button("🗑️ Confirm Delete"):
                db.delete_raw_material(m["material_id"])
                st.success("✅ Material deleted.")
                st.rerun()

    with tab_recipe:
        st.subheader("🧪 Recipe — Ingredients per Chocolate Piece")
        st.info(
            "🔄 This recipe is used **automatically** every time a production batch is recorded. "
            "The system deducts `quantity_produced × qty_per_unit` from each ingredient's stock."
        )

        products = db.get_all_products()
        if not products:
            st.error("No products found. Add a product first.")
        else:
            prod_opts = {p["name"]: p["product_id"] for p in products}
            sel_product = st.selectbox("Product", list(prod_opts.keys()), key="recipe_product")
            pid = prod_opts[sel_product]

            recipe_rows = db.get_product_recipe(pid)

            # --- View / Edit existing recipe ---
            if recipe_rows:
                st.markdown("#### Current Recipe")
                for row in recipe_rows:
                    col_mat, col_qty, col_unit, col_save, col_del = st.columns([3, 2, 1, 1, 1])
                    col_mat.markdown(f"**{row['material_name']}**")
                    new_qty = col_qty.number_input(
                        "Qty/pc",
                        min_value=0.000001,
                        value=float(row["qty_per_unit"]),
                        format="%f",
                        key=f"rqty_{row['recipe_id']}",
                        label_visibility="collapsed",
                    )
                    col_unit.markdown(f"*{row['unit']}*")
                    if col_save.button("💾", key=f"rsave_{row['recipe_id']}", help="Save"):
                        db.upsert_recipe_item(pid, row["material_id"], new_qty)
                        st.success(f"✅ Updated {row['material_name']}")
                        st.rerun()
                    if col_del.button("🗑️", key=f"rdel_{row['recipe_id']}", help="Remove"):
                        db.delete_recipe_item(row["recipe_id"])
                        st.warning(f"Removed {row['material_name']} from recipe.")
                        st.rerun()
            else:
                st.warning("No recipe defined yet for this product.")

            st.markdown("---")
            st.markdown("#### Add Ingredient to Recipe")
            materials_all = db.get_all_raw_materials()
            # Filter out materials already in recipe
            existing_mat_ids = {r["material_id"] for r in recipe_rows}
            available_mats = [m for m in materials_all if m["material_id"] not in existing_mat_ids]

            if available_mats:
                with st.form("add_recipe_form", clear_on_submit=True):
                    mat_opts = {f"{m['name']} ({m['unit']})": m for m in available_mats}
                    sel_mat = st.selectbox("Ingredient", list(mat_opts.keys()))
                    add_qty = st.number_input(
                        "Quantity per chocolate piece",
                        min_value=0.000001, value=0.01, format="%f"
                    )
                    if st.form_submit_button("➕ Add to Recipe"):
                        mat = mat_opts[sel_mat]
                        db.upsert_recipe_item(pid, mat["material_id"], add_qty)
                        st.success(f"✅ {mat['name']} added to recipe ({add_qty} {mat['unit']}/pc)")
                        st.rerun()
            else:
                st.info("✅ All available raw materials are already in the recipe.")


#  PAGE 4 – PRODUCTION BATCHES
elif page == "⚙️  Production Batches":
    st.markdown(
        """<div class='page-banner'>
            <h1>⚙️ Production Batch Recording</h1>
            <p>Record daily manufacturing batches — inventory is updated automatically via database trigger</p>
        </div>""",
        unsafe_allow_html=True,
    )

    tab_view, tab_add, tab_edit, tab_del = st.tabs(
        ["📋 All Batches", "➕ Record Batch", "✏️ Edit Batch", "🗑️ Delete Batch"]
    )

    with tab_view:
        batches = db.get_all_batches()
        if batches:
            df = pd.DataFrame(batches)
            display = ["batch_id", "production_date", "batch_number", "quantity_produced", "notes", "product_name"]
            df = df[display]
            df.columns = ["Batch ID", "Date", "Batch #", "Qty Produced", "Notes", "Product"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No production batches recorded yet.")

    with tab_add:
        st.subheader("Record a Production Batch")
        products = db.get_all_products()
        if not products:
            st.error("No products in the database. Please add a product first.")
        else:
            prod_opts = {p["name"]: p["product_id"] for p in products}
            # Lock production date to today — no past/future dates allowed
            prod_date = date.today()
            st.info(f"📅 Production Date: **{prod_date}** (only today’s batches can be recorded)")

            # Show expected raw material deduction
            sel_product_name = list(prod_opts.keys())[0]
            sel_pid = prod_opts[sel_product_name]
            recipe_preview = db.get_product_recipe(sel_pid)
            if recipe_preview:
                with st.expander("🧪 Raw material deduction preview (per unit produced)", expanded=False):
                    for rr in recipe_preview:
                        st.caption(f"• **{rr['material_name']}**: {rr['qty_per_unit']} {rr['unit']} per piece")
                    st.caption("⚡ Actual deduction = qty_per_unit × quantity_produced, applied automatically on save.")

            existing  = db.get_existing_batch_numbers(prod_date)
            available = [b for b in [1, 2] if b not in existing]
            with st.form("add_batch_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                product_name = col1.selectbox("Product", list(prod_opts.keys()))
                if not available:
                    st.warning(
                        f"⚠️ Both batches (1 & 2) already recorded for **{prod_date}**. "
                        "Edit an existing batch if a correction is needed."
                    )
                    batch_num = col2.selectbox("Batch Number", [1, 2], disabled=True)
                else:
                    batch_num = col2.selectbox("Batch Number", available)
                qty   = col1.number_input("Quantity Produced (pcs)", min_value=1, step=1)
                notes = st.text_area("Notes (optional)", placeholder="e.g., Morning shift, Machine A")
                submitted = st.form_submit_button("⚙️ Record Batch")
                if submitted:
                    if not available:
                        st.error("❌ Both batches are already recorded for today.")
                    else:
                        db.add_production_batch(
                            prod_opts[product_name], prod_date, batch_num, qty, notes
                        )
                        st.success(
                            f"✅ Batch {batch_num} for **{prod_date}** recorded — "
                            f"**{qty:,}** chocolates. Inventory & raw materials updated automatically! 🍫"
                        )
                        st.rerun()

    with tab_edit:
        st.subheader("Edit Today's Production Batch")
        today_batches = db.get_batches_by_date(date.today())
        if not today_batches:
            st.info("📭 No batches recorded for today.")
        else:
            opts = {
                f"Batch {b['batch_number']} — {b['production_date']} ({b['quantity_produced']} pcs)": b
                for b in today_batches
            }
            choice = st.selectbox("Select Batch to Edit", list(opts.keys()))
            B = opts[choice]
            with st.form("edit_batch_form"):
                new_qty   = st.number_input("Quantity Produced", min_value=1, value=int(B["quantity_produced"]))
                new_notes = st.text_area("Notes", value=B["notes"] or "")
                if st.form_submit_button("💾 Update Batch"):
                    db.update_production_batch(B["batch_id"], new_qty, new_notes)
                    st.success("✅ Batch updated. Inventory total adjusted automatically via trigger.")
                    st.rerun()

    with tab_del:
        st.subheader("Delete Today's Production Batch")
        today_batches = db.get_batches_by_date(date.today())
        if not today_batches:
            st.info("📭 No batches recorded for today.")
        else:
            opts = {
                f"Batch {b['batch_number']} — {b['production_date']} ({b['quantity_produced']} pcs)": b
                for b in today_batches
            }
            choice = st.selectbox("Select Batch to Delete", list(opts.keys()))
            B = opts[choice]
            st.warning(f"⚠️ This will permanently delete **Batch {B['batch_number']}** ({B['quantity_produced']} pcs). Inventory will be reduced automatically.")
            if st.button("🗑️ Delete Batch"):
                qty_removed = int(B["quantity_produced"])
                db.delete_production_batch(B["batch_id"])
                st.success(f"✅ Batch deleted. Inventory reduced by **{qty_removed:,} pcs** automatically.")
                st.rerun()


#  PAGE 5 – INVENTORY MONITORING
elif page == "📦  Inventory Monitoring":
    st.markdown(
        """<div class='page-banner'>
            <h1>📦 Inventory Monitoring</h1>
            <p>Daily production totals — auto-updated by database trigger</p>
        </div>""",
        unsafe_allow_html=True,
    )

    col_f, col_sp = st.columns([1, 3])
    filter_date = col_f.date_input("Filter by Date (optional)", value=None)

    if filter_date:
        rows = db.get_inventory_by_date(filter_date)
        st.subheader(f"Inventory for {filter_date}")
    else:
        rows = db.get_all_inventory()
        st.subheader("All Inventory Records")

    if rows:
        df = pd.DataFrame(rows)
        cols = ["inventory_date", "product_name", "total_quantity", "unit_weight", "total_weight_kg"]
        available_cols = [c for c in cols if c in df.columns]
        df = df[available_cols]
        rename = {
            "inventory_date": "Date",
            "product_name":   "Product",
            "total_quantity": "Total Pieces",
            "unit_weight":    "Weight/pc (g)",
            "total_weight_kg":"Total Weight (kg)",
        }
        df.rename(columns=rename, inplace=True)

        st.dataframe(df, use_container_width=True, hide_index=True)

        if "Total Pieces" in df.columns and len(df) > 1:
            st.markdown("---")
            st.subheader("📈 Inventory Trend")
            fig2 = px.line(
                df, x="Date", y="Total Pieces",
                markers=True,
                color_discrete_sequence=["#3fb950"],
                template="plotly_dark",
                labels={"Date": "Date", "Total Pieces": "Chocolates in Inventory"},
            )
            fig2.update_layout(
                plot_bgcolor="#161b22", paper_bgcolor="#161b22",
                font=dict(color="#e6edf3"),
                xaxis=dict(gridcolor="#30363d"),
                yaxis=dict(gridcolor="#30363d"),
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No inventory records found.")


#  PAGE 6 – REPORTS
elif page == "📊  Reports":
    st.markdown(
        """<div class='page-banner'>
            <h1>📊 Reports & Analytics</h1>
            <p>Date-range filtered production analysis</p>
        </div>""",
        unsafe_allow_html=True,
    )

    tab_prod, tab_inv, tab_rm, tab_summary = st.tabs(
        ["⚙️ Production Report", "📦 Inventory Report", "🥄 Raw Material Report", "🔢 Summary Stats"]
    )

    with tab_prod:
        st.subheader("Production Report by Date Range")
        col1, col2 = st.columns(2)
        start = col1.date_input("Start Date", value=date.today() - timedelta(days=7))
        end   = col2.date_input("End Date",   value=date.today())
        if st.button("🔍 Generate Production Report"):
            if start > end:
                st.error("Start date must be before end date.")
            else:
                batches = db.get_batches_by_date_range(start, end)
                if batches:
                    df = pd.DataFrame(batches)
                    df = df[["production_date", "batch_number", "quantity_produced", "notes", "product_name"]]
                    df.columns = ["Date", "Batch #", "Qty Produced", "Notes", "Product"]
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    total = int(df["Qty Produced"].sum())
                    st.markdown(f"### 🍫 Total produced ({start} → {end}): **{total:,} chocolates**")

                    fig3 = px.bar(
                        df, x="Date", y="Qty Produced", color="Batch #",
                        barmode="stack",
                        color_discrete_sequence=["#f0883e", "#3fb950"],
                        template="plotly_dark",
                        text="Qty Produced",
                    )
                    fig3.update_layout(
                        plot_bgcolor="#161b22", paper_bgcolor="#161b22",
                        font=dict(color="#e6edf3"),
                        xaxis=dict(gridcolor="#30363d"),
                        yaxis=dict(gridcolor="#30363d"),
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("No production batches found in that date range.")

    with tab_inv:
        st.subheader("Inventory Report by Date Range")
        col1, col2 = st.columns(2)
        start_i = col1.date_input("Start Date", value=date.today() - timedelta(days=7), key="inv_start")
        end_i   = col2.date_input("End Date",   value=date.today(),                    key="inv_end")
        if st.button("🔍 Generate Inventory Report"):
            rows = db.get_inventory_by_date_range(start_i, end_i)
            if rows:
                df = pd.DataFrame(rows)
                df.columns = ["Date", "Product", "Total Pieces", "Total Weight (kg)"]
                st.dataframe(df, use_container_width=True, hide_index=True)
                grand = int(df["Total Pieces"].sum())
                kg    = df["Total Weight (kg)"].sum()
                st.markdown(
                    f"### 📦 Total: **{grand:,} pieces** ({kg:.2f} kg)"
                )
            else:
                st.info("No inventory records in that range.")

    with tab_rm:
        st.subheader("Raw Material Stock Levels")
        materials = db.get_all_raw_materials()
        if materials:
            df = pd.DataFrame(materials)
            df = df[["name", "unit", "quantity", "reorder_level", "supplier_name"]]
            df.columns = ["Material", "Unit", "In Stock", "Reorder Level", "Supplier"]

            fig4 = px.bar(
                df, x="Material", y="In Stock",
                color="In Stock",
                color_continuous_scale=["#d62728", "#f0883e", "#3fb950"],
                template="plotly_dark",
                text="In Stock",
            )
            fig4.update_layout(
                plot_bgcolor="#161b22", paper_bgcolor="#161b22",
                font=dict(color="#e6edf3"),
                coloraxis_showscale=False,
                xaxis=dict(gridcolor="#30363d"),
                yaxis=dict(gridcolor="#30363d"),
            )
            st.plotly_chart(fig4, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No raw materials found.")

    with tab_summary:
        st.subheader("Overall Production Summary")
        batches = db.get_all_batches()
        if batches:
            df = pd.DataFrame(batches)
            df["quantity_produced"] = df["quantity_produced"].astype(int)
            summary = (
                df.groupby("production_date")["quantity_produced"]
                .agg(["sum", "count", "min", "max"])
                .reset_index()
            )
            summary.columns = ["Date", "Total Produced", "Batches Run", "Min Batch", "Max Batch"]
            st.dataframe(summary, use_container_width=True, hide_index=True)

            grand = int(df["quantity_produced"].sum())
            avg   = grand / len(summary) if len(summary) > 0 else 0
            col1, col2, col3 = st.columns(3)
            col1.metric("🍫 Grand Total", f"{grand:,}")
            col2.metric("📅 Days Recorded", len(summary))
            col3.metric("📊 Avg per Day", f"{avg:,.0f}")
        else:
            st.info("No production data yet.")