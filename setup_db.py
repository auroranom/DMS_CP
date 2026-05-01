"""
setup_db.py  –  One-time database setup script
Run with:  python setup_db.py
"""
import mysql.connector
from mysql.connector import Error

import os

DB_HOST = os.environ.get("MYSQL_HOST", "localhost")
DB_PORT = int(os.environ.get("MYSQL_PORT", 3306))
DB_USER = os.environ.get("MYSQL_USER", "root")
DB_PASS = os.environ.get("MYSQL_PASS", "Harshu@19")
DB_NAME = os.environ.get("MYSQL_DB", "nutchoc_db")


def run(cur, sql):
    """Execute one statement, ignore 'already exists' style errors."""
    try:
        cur.execute(sql)
    except Error as e:
        print(f"  ⚠  {e}")


def main():
    print("=" * 54)
    print("   NutChoc DB Setup")
    print("=" * 54)

    try:
        conn = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS
        )
    except Error as e:
        print(f"✗ Cannot connect: {e}")
        return

    conn.autocommit = True
    cur = conn.cursor()

    # ── 1. Create & select database ──────────────────────────
    run(cur, f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    run(cur, f"USE {DB_NAME}")
    print(f"✓ Database: {DB_NAME}")

    # ── 2. Create tables ─────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Supplier (
            supplier_id   INT          NOT NULL AUTO_INCREMENT,
            name          VARCHAR(100) NOT NULL,
            contact_phone VARCHAR(15),
            email         VARCHAR(100),
            address       VARCHAR(255),
            PRIMARY KEY (supplier_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS RawMaterial (
            material_id   INT NOT NULL AUTO_INCREMENT,
            name          VARCHAR(100) NOT NULL,
            unit          VARCHAR(20)  NOT NULL,
            quantity      DECIMAL(10,2) NOT NULL DEFAULT 0,
            reorder_level DECIMAL(10,2) NOT NULL DEFAULT 0,
            supplier_id   INT,
            PRIMARY KEY (material_id),
            CONSTRAINT fk_rm_supplier
                FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
                ON DELETE SET NULL ON UPDATE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Product (
            product_id  INT NOT NULL AUTO_INCREMENT,
            name        VARCHAR(100) NOT NULL,
            description TEXT,
            unit_weight DECIMAL(6,2) NOT NULL DEFAULT 0,
            PRIMARY KEY (product_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ProductionBatch (
            batch_id          INT NOT NULL AUTO_INCREMENT,
            product_id        INT NOT NULL,
            production_date   DATE NOT NULL,
            batch_number      TINYINT NOT NULL,
            quantity_produced INT NOT NULL DEFAULT 0,
            notes             VARCHAR(255),
            PRIMARY KEY (batch_id),
            UNIQUE KEY uq_date_batch (production_date, batch_number),
            CONSTRAINT fk_pb_product
                FOREIGN KEY (product_id) REFERENCES Product(product_id)
                ON DELETE RESTRICT ON UPDATE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Inventory (
            inventory_id   INT NOT NULL AUTO_INCREMENT,
            product_id     INT NOT NULL,
            inventory_date DATE NOT NULL,
            total_quantity INT NOT NULL DEFAULT 0,
            PRIMARY KEY (inventory_id),
            UNIQUE KEY uq_inv_date (product_id, inventory_date),
            CONSTRAINT fk_inv_product
                FOREIGN KEY (product_id) REFERENCES Product(product_id)
                ON DELETE RESTRICT ON UPDATE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS supply_requests (
            id          INT NOT NULL AUTO_INCREMENT,
            supplier_id INT NOT NULL,
            item_name   VARCHAR(150) NOT NULL,
            quantity    DECIMAL(10,2) NOT NULL,
            unit        VARCHAR(20) NOT NULL DEFAULT 'kg',
            supply_date DATE,
            notes       TEXT,
            status      ENUM('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending',
            created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            CONSTRAINT fk_sr_supplier
                FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ProductRecipe (
            recipe_id      INT NOT NULL AUTO_INCREMENT,
            product_id     INT NOT NULL,
            material_id    INT NOT NULL,
            qty_per_unit   DECIMAL(12,6) NOT NULL DEFAULT 0,
            PRIMARY KEY (recipe_id),
            UNIQUE KEY uq_recipe (product_id, material_id),
            CONSTRAINT fk_recipe_product
                FOREIGN KEY (product_id) REFERENCES Product(product_id)
                ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fk_recipe_material
                FOREIGN KEY (material_id) REFERENCES RawMaterial(material_id)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INT          NOT NULL AUTO_INCREMENT,
            username    VARCHAR(50)  NOT NULL UNIQUE,
            password    VARCHAR(255) NOT NULL,
            role        ENUM('manager','supplier') NOT NULL,
            supplier_id INT DEFAULT NULL,
            PRIMARY KEY (id),
            CONSTRAINT fk_users_supplier
                FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
                ON DELETE SET NULL ON UPDATE CASCADE
        )
    """)
    print("\u2713 Tables created / verified (users + supply_requests + ProductRecipe included)")

    # ── 3. Triggers ──────────────────────────────────────────
    run(cur, "DROP TRIGGER IF EXISTS after_batch_insert")
    cur.execute("""
        CREATE TRIGGER after_batch_insert
        AFTER INSERT ON ProductionBatch
        FOR EACH ROW
        BEGIN
            -- 1. Update Inventory
            INSERT INTO Inventory (product_id, inventory_date, total_quantity)
            VALUES (NEW.product_id, NEW.production_date, NEW.quantity_produced)
            ON DUPLICATE KEY UPDATE
                total_quantity = total_quantity + NEW.quantity_produced;

            -- 2. Deduct raw materials based on recipe
            UPDATE RawMaterial rm
            JOIN ProductRecipe pr
                ON pr.material_id = rm.material_id
               AND pr.product_id  = NEW.product_id
            SET rm.quantity = GREATEST(0, rm.quantity - (NEW.quantity_produced * pr.qty_per_unit));
        END
    """)

    run(cur, "DROP TRIGGER IF EXISTS after_batch_update")
    cur.execute("""
        CREATE TRIGGER after_batch_update
        AFTER UPDATE ON ProductionBatch
        FOR EACH ROW
        BEGIN
            -- 1. Adjust Inventory
            UPDATE Inventory
            SET total_quantity = total_quantity - OLD.quantity_produced + NEW.quantity_produced
            WHERE product_id    = NEW.product_id
              AND inventory_date = NEW.production_date;

            -- 2. Compensate raw material: add back old qty, subtract new qty
            UPDATE RawMaterial rm
            JOIN ProductRecipe pr
                ON pr.material_id = rm.material_id
               AND pr.product_id  = NEW.product_id
            SET rm.quantity = GREATEST(0,
                rm.quantity
                + (OLD.quantity_produced * pr.qty_per_unit)
                - (NEW.quantity_produced * pr.qty_per_unit)
            );
        END
    """)
    print("\u2713 Triggers created (with raw material auto-deduction)")

    # ── 4. Seed data (only if tables are empty) ───────────────
    cur.execute("SELECT COUNT(*) FROM Supplier")
    if cur.fetchone()[0] == 0:
        suppliers = [
            ('ChocoCraft Suppliers', '9876543210', 'chococraft@example.com', '12 Cocoa Lane, Mumbai'),
            ('NutriNuts Pvt. Ltd.',  '9123456780', 'nutrinuts@example.com',  '45 Almond Street, Pune'),
            ('SweetPack Industries', '9988776655', 'sweetpack@example.com',  '8 Sugar Park, Nashik'),
        ]
        cur.executemany(
            "INSERT INTO Supplier (name,contact_phone,email,address) VALUES (%s,%s,%s,%s)",
            suppliers
        )

    cur.execute("SELECT COUNT(*) FROM RawMaterial")
    if cur.fetchone()[0] == 0:
        materials = [
            ('Compound Chocolate',  'kg',  250.00, 50.00,  1),
            ('Cocoa Powder',        'kg',  120.00, 30.00,  1),
            ('Sugar',               'kg',  300.00, 60.00,  3),
            ('Milk Powder',         'kg',  180.00, 40.00,  3),
            ('Crushed Cashew Nuts', 'kg',  100.00, 25.00,  2),
            ('Roasted Almonds',     'kg',   80.00, 20.00,  2),
            ('Aluminium Foil',      'pcs', 5000.00,500.00, 3),
            ('Cardboard Boxes',     'pcs', 2000.00,200.00, 3),
        ]
        cur.executemany(
            "INSERT INTO RawMaterial (name,unit,quantity,reorder_level,supplier_id) VALUES (%s,%s,%s,%s,%s)",
            materials
        )

    cur.execute("SELECT COUNT(*) FROM Product")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO Product (name,description,unit_weight) VALUES (%s,%s,%s)",
            ('Nut Chocolate',
             'Premium milk chocolate bar enriched with crushed cashews and roasted almonds.',
             50.00)
        )

    # Seed ProductRecipe – only if empty (use name-based lookup to avoid FK issues)
    cur.execute("SELECT COUNT(*) FROM ProductRecipe")
    if cur.fetchone()[0] == 0:
        # Look up product_id for 'Nut Chocolate' dynamically
        cur.execute("SELECT product_id FROM Product WHERE name = 'Nut Chocolate' LIMIT 1")
        prod_row = cur.fetchone()
        if prod_row:
            prod_id = prod_row[0]
            # Ingredient name -> qty_per_unit consumed per 1 chocolate piece (50g bar)
            recipe_spec = {
                'Compound Chocolate':  0.025,   # kg
                'Cocoa Powder':        0.005,   # kg
                'Sugar':               0.008,   # kg
                'Milk Powder':         0.007,   # kg
                'Crushed Cashew Nuts': 0.003,   # kg
                'Roasted Almonds':     0.002,   # kg
                'Aluminium Foil':      1.0,     # pcs
                'Cardboard Boxes':     0.1,     # pcs
            }
            seeded = 0
            for mat_name, qty in recipe_spec.items():
                cur.execute(
                    "SELECT material_id FROM RawMaterial WHERE name = %s LIMIT 1",
                    (mat_name,)
                )
                mat_row = cur.fetchone()
                if mat_row:
                    cur.execute(
                        """INSERT INTO ProductRecipe (product_id, material_id, qty_per_unit)
                           VALUES (%s, %s, %s)
                           ON DUPLICATE KEY UPDATE qty_per_unit = VALUES(qty_per_unit)""",
                        (prod_id, mat_row[0], qty)
                    )
                    seeded += 1
                else:
                    print(f"  -- Skipped '{mat_name}' (not found in RawMaterial)")
            print(f"\u2713 Product recipe seeded ({seeded} ingredients)")

    cur.execute("SELECT COUNT(*) FROM ProductionBatch")
    if cur.fetchone()[0] == 0:
        batches = [
            (1, '2026-03-10', 1, 500, 'Morning batch – machine A'),
            (1, '2026-03-10', 2, 480, 'Evening batch – machine B'),
            (1, '2026-03-11', 1, 520, 'Morning batch – machine A'),
            (1, '2026-03-11', 2, 510, 'Evening batch – machine B'),
            (1, '2026-03-12', 1, 490, 'Morning batch – production as usual'),
            (1, '2026-03-12', 2, 505, 'Evening batch – slight delay'),
        ]
        cur.executemany(
            "INSERT INTO ProductionBatch (product_id,production_date,batch_number,quantity_produced,notes) VALUES (%s,%s,%s,%s,%s)",
            batches
        )

    # Seed users – only if table is empty
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        users_data = [
            ('manager1',  'manager123',  'manager',  None),
            ('chococraft', 'supplier123', 'supplier', 1),
            ('nutrinuts',  'supplier123', 'supplier', 2),
            ('sweetpack',  'supplier123', 'supplier', 3),
        ]
        cur.executemany(
            "INSERT INTO users (username, password, role, supplier_id) VALUES (%s,%s,%s,%s)",
            users_data
        )
        print("\u2713 Default users seeded (manager1 + 3 suppliers)")
    print("\u2713 Seed data inserted")

    # ── 5. Verify ────────────────────────────────────────────
    print("\n" + "-" * 40)
    for table in ["Supplier", "RawMaterial", "Product", "ProductionBatch", "Inventory", "users", "supply_requests", "ProductRecipe"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        cnt = cur.fetchone()[0]
        print(f"  {table:20s}: {cnt:>3} rows")
    cur.execute("SHOW TRIGGERS LIKE 'after_batch_%'")
    triggers = cur.fetchall()
    print(f"\n  Triggers: {', '.join(t[0] for t in triggers)}")
    cur.close()
    conn.close()
    print("\n✅ Done! Run:  streamlit run app.py")


if __name__ == "__main__":
    main()
