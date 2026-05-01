"""
db.py – MySQL database connection and CRUD helpers
Nut Chocolate Production & Inventory Management System
"""

import mysql.connector
from mysql.connector import Error
import streamlit as st

#  DB config — reads from Streamlit secrets (cloud) or falls back to local
try:
    DB_CONFIG = {
        "host":     st.secrets["mysql"]["host"],
        "port":     int(st.secrets["mysql"]["port"]),
        "user":     st.secrets["mysql"]["user"],
        "password": st.secrets["mysql"]["password"],
        "database": st.secrets["mysql"]["database"],
        "ssl_disabled": False,
    }
except Exception:
    DB_CONFIG = {
        "host":     "localhost",
        "user":     "root",
        "password": "Harshu@19",      
        "database": "nutchoc_db",
    }

#  Connection 
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None


def run_query(sql: str, params=None, fetch=True):
    """Execute a SELECT query and return rows as list-of-dicts."""
    conn = get_connection()
    if conn is None:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            return cur.fetchall()
        conn.commit()
        return []
    except Error as e:
        st.error(f"Query error: {e}")
        return []
    finally:
        conn.close()


def run_mutation(sql: str, params=None):
    """Execute INSERT / UPDATE / DELETE and return last-row-id."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.lastrowid
    except Error as e:
        st.error(f"Mutation error: {e}")
        return None
    finally:
        conn.close()


#  SUPPLIER
def get_all_suppliers():
    return run_query("SELECT * FROM Supplier ORDER BY name")


def add_supplier(name, phone, email, address):
    return run_mutation(
        "INSERT INTO Supplier (name, contact_phone, email, address) VALUES (%s,%s,%s,%s)",
        (name, phone, email, address),
    )


def delete_supplier(supplier_id):
    return run_mutation("DELETE FROM Supplier WHERE supplier_id=%s", (supplier_id,))


def update_supplier(supplier_id, name, phone, email, address):
    return run_mutation(
        """UPDATE Supplier
           SET name=%s, contact_phone=%s, email=%s, address=%s
           WHERE supplier_id=%s""",
        (name, phone, email, address, supplier_id),
    )


#  RAW MATERIAL
def get_all_raw_materials():
    return run_query(
        """SELECT rm.*, s.name AS supplier_name
           FROM RawMaterial rm
           LEFT JOIN Supplier s ON s.supplier_id = rm.supplier_id
           ORDER BY rm.name"""
    )


def add_raw_material(name, unit, quantity, reorder_level, supplier_id):
    return run_mutation(
        """INSERT INTO RawMaterial
           (name, unit, quantity, reorder_level, supplier_id)
           VALUES (%s,%s,%s,%s,%s)""",
        (name, unit, quantity, reorder_level, supplier_id or None),
    )


def update_raw_material_stock(material_id, quantity):
    return run_mutation(
        "UPDATE RawMaterial SET quantity=%s WHERE material_id=%s",
        (quantity, material_id),
    )


def delete_raw_material(material_id):
    return run_mutation("DELETE FROM RawMaterial WHERE material_id=%s", (material_id,))


def get_low_stock_materials():
    return run_query(
        """SELECT rm.name, rm.quantity, rm.reorder_level, s.name AS supplier_name
           FROM RawMaterial rm
           LEFT JOIN Supplier s ON s.supplier_id = rm.supplier_id
           WHERE rm.quantity <= rm.reorder_level"""
    )


#  PRODUCT
def get_all_products():
    return run_query("SELECT * FROM Product ORDER BY name")


def add_product(name, description, unit_weight):
    return run_mutation(
        "INSERT INTO Product (name, description, unit_weight) VALUES (%s,%s,%s)",
        (name, description, unit_weight),
    )


#  PRODUCTION BATCH
def get_all_batches():
    return run_query(
        """SELECT pb.*, p.name AS product_name
           FROM ProductionBatch pb
           JOIN Product p ON p.product_id = pb.product_id
           ORDER BY pb.production_date DESC, pb.batch_number"""
    )


def get_batches_by_date(date):
    return run_query(
        """SELECT pb.*, p.name AS product_name
           FROM ProductionBatch pb
           JOIN Product p ON p.product_id = pb.product_id
           WHERE pb.production_date = %s
           ORDER BY pb.batch_number""",
        (date,),
    )


def get_batches_by_date_range(start_date, end_date):
    return run_query(
        """SELECT pb.*, p.name AS product_name
           FROM ProductionBatch pb
           JOIN Product p ON p.product_id = pb.product_id
           WHERE pb.production_date BETWEEN %s AND %s
           ORDER BY pb.production_date, pb.batch_number""",
        (start_date, end_date),
    )


def add_production_batch(product_id, production_date, batch_number, quantity, notes):
    return run_mutation(
        """INSERT INTO ProductionBatch
           (product_id, production_date, batch_number, quantity_produced, notes)
           VALUES (%s,%s,%s,%s,%s)""",
        (product_id, production_date, batch_number, quantity, notes),
    )


def update_production_batch(batch_id, quantity, notes):
    return run_mutation(
        "UPDATE ProductionBatch SET quantity_produced=%s, notes=%s WHERE batch_id=%s",
        (quantity, notes, batch_id),
    )


def delete_production_batch(batch_id):
    """Delete a production batch.
    - If this is the ONLY batch for that date → DELETE the Inventory row entirely.
    - If another batch still exists for that date → SUBTRACT this batch's quantity from Inventory.
    """
    conn = get_connection()
    if conn is None:
        return None
    try:
        cur = conn.cursor(dictionary=True)

        # 1. Fetch the batch to know its product, date and quantity
        cur.execute(
            "SELECT product_id, production_date, quantity_produced FROM ProductionBatch WHERE batch_id = %s",
            (batch_id,),
        )
        row = cur.fetchone()

        if row:
            product_id    = row["product_id"]
            prod_date     = row["production_date"]
            qty           = row["quantity_produced"]

            # 2. Count how many OTHER batches exist for the same product+date
            cur.execute(
                """SELECT COUNT(*) AS cnt FROM ProductionBatch
                   WHERE product_id = %s AND production_date = %s AND batch_id != %s""",
                (product_id, prod_date, batch_id),
            )
            others = cur.fetchone()["cnt"]

            if others == 0:
                # Last batch for this date → remove the entire inventory row
                cur.execute(
                    "DELETE FROM Inventory WHERE product_id = %s AND inventory_date = %s",
                    (product_id, prod_date),
                )
            else:
                # Another batch exists → just subtract this batch's quantity
                cur.execute(
                    """UPDATE Inventory
                       SET total_quantity = GREATEST(0, total_quantity - %s)
                       WHERE product_id = %s AND inventory_date = %s""",
                    (qty, product_id, prod_date),
                )

        # 3. Delete the production batch row itself
        cur.execute("DELETE FROM ProductionBatch WHERE batch_id = %s", (batch_id,))
        conn.commit()
        return cur.lastrowid

    except Exception as e:
        st.error(f"Mutation error: {e}")
        return None
    finally:
        conn.close()




def get_existing_batch_numbers(production_date):
    rows = run_query(
        "SELECT batch_number FROM ProductionBatch WHERE production_date=%s",
        (production_date,),
    )
    return [r["batch_number"] for r in rows]


#  INVENTORY
def get_all_inventory():
    return run_query(
        """SELECT i.*, p.name AS product_name, p.unit_weight,
                  ROUND(i.total_quantity * p.unit_weight / 1000, 2) AS total_weight_kg
           FROM Inventory i
           JOIN Product p ON p.product_id = i.product_id
           ORDER BY i.inventory_date DESC"""
    )


def get_inventory_by_date(date):
    return run_query(
        """SELECT i.*, p.name AS product_name
           FROM Inventory i
           JOIN Product p ON p.product_id = i.product_id
           WHERE i.inventory_date = %s""",
        (date,),
    )


def get_inventory_by_date_range(start_date, end_date):
    return run_query(
        """SELECT i.inventory_date, p.name AS product_name, i.total_quantity,
                  ROUND(i.total_quantity * p.unit_weight / 1000, 2) AS total_weight_kg
           FROM Inventory i
           JOIN Product p ON p.product_id = i.product_id
           WHERE i.inventory_date BETWEEN %s AND %s
           ORDER BY i.inventory_date""",
        (start_date, end_date),
    )


#  DASHBOARD STATS
def get_dashboard_stats():
    stats = {}
    r = run_query("SELECT COUNT(*) AS cnt FROM Supplier")
    stats["total_suppliers"] = r[0]["cnt"] if r else 0

    r = run_query("SELECT COUNT(*) AS cnt FROM RawMaterial")
    stats["total_materials"] = r[0]["cnt"] if r else 0

    r = run_query("SELECT COUNT(*) AS cnt FROM ProductionBatch")
    stats["total_batches"] = r[0]["cnt"] if r else 0

    r = run_query("SELECT COALESCE(SUM(total_quantity),0) AS s FROM Inventory")
    stats["grand_total_produced"] = int(r[0]["s"]) if r else 0

    r = run_query(
        """SELECT COALESCE(SUM(quantity_produced),0) AS s
           FROM ProductionBatch WHERE production_date = CURDATE()"""
    )
    stats["today_produced"] = int(r[0]["s"]) if r else 0

    r = run_query("SELECT COUNT(*) AS cnt FROM RawMaterial WHERE quantity <= reorder_level")
    stats["low_stock_count"] = r[0]["cnt"] if r else 0
    return stats


def get_daily_production_chart_data():
    return run_query(
        """SELECT production_date AS date,
                  SUM(quantity_produced) AS total
           FROM ProductionBatch
           GROUP BY production_date
           ORDER BY production_date"""
    )


# ─── PRODUCT RECIPE ────────────────────────────────────────────────────────────
def get_product_recipe(product_id):
    """Return all recipe rows for a given product, joined with material names."""
    return run_query(
        """SELECT pr.recipe_id, rm.material_id, rm.name AS material_name,
                  rm.unit, pr.qty_per_unit
           FROM ProductRecipe pr
           JOIN RawMaterial rm ON rm.material_id = pr.material_id
           WHERE pr.product_id = %s
           ORDER BY rm.name""",
        (product_id,)
    )


def get_all_recipe_items():
    """Return all recipe rows across all products (for manager overview)."""
    return run_query(
        """SELECT pr.recipe_id, p.name AS product_name, rm.name AS material_name,
                  rm.unit, pr.qty_per_unit
           FROM ProductRecipe pr
           JOIN Product p       ON p.product_id    = pr.product_id
           JOIN RawMaterial rm  ON rm.material_id  = pr.material_id
           ORDER BY p.name, rm.name"""
    )


def upsert_recipe_item(product_id, material_id, qty_per_unit):
    """Insert or update a recipe entry (qty consumed per 1 unit produced)."""
    return run_mutation(
        """INSERT INTO ProductRecipe (product_id, material_id, qty_per_unit)
           VALUES (%s, %s, %s)
           ON DUPLICATE KEY UPDATE qty_per_unit = VALUES(qty_per_unit)""",
        (product_id, material_id, qty_per_unit)
    )


def delete_recipe_item(recipe_id):
    """Remove a recipe ingredient entry."""
    return run_mutation(
        "DELETE FROM ProductRecipe WHERE recipe_id = %s",
        (recipe_id,)
    )

# ─── SUPPLY REQUESTS ───────────────────────────────────────────────────────────
def get_supplier_requests(supplier_id):
    """Get ALL supply requests for a specific supplier (full history)."""
    return run_query(
        """SELECT id, item_name, quantity, unit, supply_date, notes, status, created_at
           FROM supply_requests
           WHERE supplier_id = %s
           ORDER BY created_at DESC""",
        (supplier_id,)
    )


def get_supplier_requests_today(supplier_id):
    """Get only TODAY's supply requests for a specific supplier."""
    return run_query(
        """SELECT id, item_name, quantity, unit, supply_date, notes, status, created_at
           FROM supply_requests
           WHERE supplier_id = %s
             AND DATE(created_at) = CURDATE()
           ORDER BY created_at DESC""",
        (supplier_id,)
    )


def get_pending_supplier_requests(supplier_id):
    """Get only PENDING supply requests for a specific supplier (editable)."""
    return run_query(
        """SELECT id, item_name, quantity, unit, supply_date, notes, status, created_at
           FROM supply_requests
           WHERE supplier_id = %s AND status = 'Pending'
           ORDER BY created_at DESC""",
        (supplier_id,)
    )


def update_supply_request(request_id, item_name, quantity, unit, supply_date, notes):
    """Update a pending supply request (only allowed while status is 'Pending')."""
    return run_mutation(
        """UPDATE supply_requests
           SET item_name = %s, quantity = %s, unit = %s, supply_date = %s, notes = %s
           WHERE id = %s AND status = 'Pending'""",
        (item_name, quantity, unit, supply_date, notes, request_id)
    )


def get_all_supply_requests():
    """Get all supply requests (for manager)."""
    return run_query(
        """SELECT sr.id, s.name AS supplier_name, sr.item_name, sr.quantity, sr.unit,
                  sr.supply_date, sr.status, sr.created_at
           FROM supply_requests sr
           JOIN Supplier s ON s.supplier_id = sr.supplier_id
           ORDER BY sr.created_at DESC"""
    )

def get_pending_requests():
    """Get pending supply requests (for manager dashboard)."""
    return run_query(
        """SELECT sr.id, s.name AS supplier_name, sr.item_name, sr.quantity, sr.unit,
                  sr.supply_date, sr.created_at
           FROM supply_requests sr
           JOIN Supplier s ON s.supplier_id = sr.supplier_id
           WHERE sr.status = 'Pending'
           ORDER BY sr.created_at DESC"""
    )

def add_supply_request(supplier_id, item_name, quantity, unit, supply_date, notes):
    """Submit a new supply request."""
    return run_mutation(
        """INSERT INTO supply_requests (supplier_id, item_name, quantity, unit, supply_date, notes)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (supplier_id, item_name, quantity, unit, supply_date, notes)
    )

def update_request_status(request_id, status):
    """Approve or reject a supply request."""
    return run_mutation(
        "UPDATE supply_requests SET status = %s WHERE id = %s",
        (status, request_id)
    )

def login_user(username, password):
    """Authenticate user and return user data if valid."""
    result = run_query(
        "SELECT id, username, role, supplier_id FROM users WHERE username = %s AND password = %s",
        (username, password)
    )
    return result[0] if result else None