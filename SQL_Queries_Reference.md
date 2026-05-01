# SQL Queries & DBMS Concepts Reference
## Nut Chocolate Production & Inventory Management System

---

## 1. DDL (Data Definition Language)

### 1.1 CREATE DATABASE
```sql
CREATE DATABASE IF NOT EXISTS nutchoc_db;
USE nutchoc_db;
```

### 1.2 CREATE TABLE (with Constraints)

**Supplier** — Primary Key, AUTO_INCREMENT, NOT NULL
```sql
CREATE TABLE IF NOT EXISTS Supplier (
    supplier_id   INT          NOT NULL AUTO_INCREMENT,
    name          VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(15),
    email         VARCHAR(100),
    address       VARCHAR(255),
    PRIMARY KEY (supplier_id)
);
```

**RawMaterial** — Primary Key, Foreign Key, ON DELETE SET NULL, ON UPDATE CASCADE, DEFAULT
```sql
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
);
```

**Product** — Primary Key, AUTO_INCREMENT, DEFAULT
```sql
CREATE TABLE IF NOT EXISTS Product (
    product_id  INT NOT NULL AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    unit_weight DECIMAL(6,2) NOT NULL DEFAULT 0,
    PRIMARY KEY (product_id)
);
```

**ProductionBatch** — Primary Key, UNIQUE KEY (Composite), Foreign Key, ON DELETE RESTRICT
```sql
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
);
```

**Inventory** — Primary Key, UNIQUE KEY (Composite), Foreign Key
```sql
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
);
```

**supply_requests** — Primary Key, ENUM data type, TIMESTAMP, DEFAULT CURRENT_TIMESTAMP, ON DELETE CASCADE
```sql
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
);
```

**ProductRecipe** — Primary Key, UNIQUE KEY (Composite), Multiple Foreign Keys, ON DELETE CASCADE
```sql
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
);
```

**users** — Primary Key, UNIQUE constraint, ENUM, Foreign Key with ON DELETE SET NULL
```sql
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
);
```

**Supplier_Contact** — Composite Primary Key (Multivalued Attribute representation)
```sql
CREATE TABLE IF NOT EXISTS Supplier_Contact (
    supplier_id INT,
    contact_no VARCHAR(15),
    PRIMARY KEY (supplier_id, contact_no),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
```

**Supplies** — M:N Relationship Table, Composite Primary Key
```sql
CREATE TABLE IF NOT EXISTS Supplies (
    supplier_id INT,
    material_id INT,
    PRIMARY KEY (supplier_id, material_id),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (material_id) REFERENCES RawMaterial(material_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);
```

### 1.3 DROP TRIGGER
```sql
DROP TRIGGER IF EXISTS after_batch_insert;
DROP TRIGGER IF EXISTS after_batch_update;
```

### 1.4 ALTER TABLE (AUTO_INCREMENT reset)
```sql
ALTER TABLE Supplier AUTO_INCREMENT = 4;
ALTER TABLE RawMaterial AUTO_INCREMENT = 9;
```

---

## 2. DML (Data Manipulation Language)

### 2.1 INSERT — Simple Insert
```sql
-- Supplier
INSERT INTO Supplier (name, contact_phone, email, address) VALUES (%s, %s, %s, %s);

-- RawMaterial
INSERT INTO RawMaterial (name, unit, quantity, reorder_level, supplier_id) VALUES (%s, %s, %s, %s, %s);

-- Product
INSERT INTO Product (name, description, unit_weight) VALUES (%s, %s, %s);

-- ProductionBatch
INSERT INTO ProductionBatch (product_id, production_date, batch_number, quantity_produced, notes)
VALUES (%s, %s, %s, %s, %s);

-- Supply Request
INSERT INTO supply_requests (supplier_id, item_name, quantity, unit, supply_date, notes)
VALUES (%s, %s, %s, %s, %s, %s);
```

### 2.2 INSERT with ON DUPLICATE KEY UPDATE (Upsert)
```sql
-- Inventory auto-update via trigger
INSERT INTO Inventory (product_id, inventory_date, total_quantity)
VALUES (NEW.product_id, NEW.production_date, NEW.quantity_produced)
ON DUPLICATE KEY UPDATE
    total_quantity = total_quantity + NEW.quantity_produced;

-- Recipe upsert
INSERT INTO ProductRecipe (product_id, material_id, qty_per_unit)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE qty_per_unit = VALUES(qty_per_unit);
```

### 2.3 UPDATE — Simple Update
```sql
-- Update supplier
UPDATE Supplier SET name=%s, contact_phone=%s, email=%s, address=%s
WHERE supplier_id=%s;

-- Update raw material stock
UPDATE RawMaterial SET quantity=%s WHERE material_id=%s;

-- Update production batch
UPDATE ProductionBatch SET quantity_produced=%s, notes=%s WHERE batch_id=%s;

-- Update supply request status (Approve/Reject)
UPDATE supply_requests SET status = %s WHERE id = %s;

-- Update pending supply request (Edit by supplier)
UPDATE supply_requests
SET item_name = %s, quantity = %s, unit = %s, supply_date = %s, notes = %s
WHERE id = %s AND status = 'Pending';
```

### 2.4 UPDATE with JOIN (Trigger-based auto-deduction)
```sql
-- Deduct raw materials based on recipe (inside trigger)
UPDATE RawMaterial rm
JOIN ProductRecipe pr
    ON pr.material_id = rm.material_id
   AND pr.product_id  = NEW.product_id
SET rm.quantity = GREATEST(0, rm.quantity - (NEW.quantity_produced * pr.qty_per_unit));
```

### 2.5 UPDATE with Arithmetic Expression (Trigger)
```sql
-- Compensate raw material on batch update
UPDATE RawMaterial rm
JOIN ProductRecipe pr
    ON pr.material_id = rm.material_id
   AND pr.product_id  = NEW.product_id
SET rm.quantity = GREATEST(0,
    rm.quantity
    + (OLD.quantity_produced * pr.qty_per_unit)
    - (NEW.quantity_produced * pr.qty_per_unit)
);

-- Inventory adjustment with GREATEST()
UPDATE Inventory
SET total_quantity = GREATEST(0, total_quantity - %s)
WHERE product_id = %s AND inventory_date = %s;
```

### 2.6 DELETE — Simple Delete
```sql
-- Delete supplier
DELETE FROM Supplier WHERE supplier_id = %s;

-- Delete raw material
DELETE FROM RawMaterial WHERE material_id = %s;

-- Delete production batch
DELETE FROM ProductionBatch WHERE batch_id = %s;

-- Delete inventory row
DELETE FROM Inventory WHERE product_id = %s AND inventory_date = %s;

-- Delete recipe item
DELETE FROM ProductRecipe WHERE recipe_id = %s;
```

---

## 3. DQL (Data Query Language)

### 3.1 SELECT — Simple Select
```sql
-- All suppliers
SELECT * FROM Supplier ORDER BY name;

-- All products
SELECT * FROM Product ORDER BY name;

-- Batch numbers for a date
SELECT batch_number FROM ProductionBatch WHERE production_date = %s;
```

### 3.2 SELECT with JOIN (INNER JOIN)
```sql
-- All batches with product name
SELECT pb.*, p.name AS product_name
FROM ProductionBatch pb
JOIN Product p ON p.product_id = pb.product_id
ORDER BY pb.production_date DESC, pb.batch_number;

-- Inventory with product details and computed weight
SELECT i.*, p.name AS product_name, p.unit_weight,
       ROUND(i.total_quantity * p.unit_weight / 1000, 2) AS total_weight_kg
FROM Inventory i
JOIN Product p ON p.product_id = i.product_id
ORDER BY i.inventory_date DESC;

-- Recipe with material names
SELECT pr.recipe_id, rm.material_id, rm.name AS material_name, rm.unit, pr.qty_per_unit
FROM ProductRecipe pr
JOIN RawMaterial rm ON rm.material_id = pr.material_id
WHERE pr.product_id = %s
ORDER BY rm.name;

-- Recipe with product and material names (Multi-table JOIN)
SELECT pr.recipe_id, p.name AS product_name, rm.name AS material_name,
       rm.unit, pr.qty_per_unit
FROM ProductRecipe pr
JOIN Product p       ON p.product_id    = pr.product_id
JOIN RawMaterial rm  ON rm.material_id  = pr.material_id
ORDER BY p.name, rm.name;

-- Supply requests with supplier name (for manager)
SELECT sr.id, s.name AS supplier_name, sr.item_name, sr.quantity, sr.unit,
       sr.supply_date, sr.status, sr.created_at
FROM supply_requests sr
JOIN Supplier s ON s.supplier_id = sr.supplier_id
ORDER BY sr.created_at DESC;

-- Pending requests with supplier name
SELECT sr.id, s.name AS supplier_name, sr.item_name, sr.quantity, sr.unit,
       sr.supply_date, sr.created_at
FROM supply_requests sr
JOIN Supplier s ON s.supplier_id = sr.supplier_id
WHERE sr.status = 'Pending'
ORDER BY sr.created_at DESC;
```

### 3.3 SELECT with LEFT JOIN
```sql
-- Raw materials with supplier name (LEFT JOIN handles NULL supplier)
SELECT rm.*, s.name AS supplier_name
FROM RawMaterial rm
LEFT JOIN Supplier s ON s.supplier_id = rm.supplier_id
ORDER BY rm.name;

-- Low stock materials with supplier
SELECT rm.name, rm.quantity, rm.reorder_level, s.name AS supplier_name
FROM RawMaterial rm
LEFT JOIN Supplier s ON s.supplier_id = rm.supplier_id
WHERE rm.quantity <= rm.reorder_level;
```

### 3.4 SELECT with WHERE — Filtering
```sql
-- Batches by exact date
SELECT pb.*, p.name AS product_name
FROM ProductionBatch pb
JOIN Product p ON p.product_id = pb.product_id
WHERE pb.production_date = %s
ORDER BY pb.batch_number;

-- Inventory by date
SELECT i.*, p.name AS product_name
FROM Inventory i
JOIN Product p ON p.product_id = i.product_id
WHERE i.inventory_date = %s;

-- Supply requests for a specific supplier
SELECT id, item_name, quantity, unit, supply_date, notes, status, created_at
FROM supply_requests
WHERE supplier_id = %s
ORDER BY created_at DESC;

-- Pending requests for a specific supplier
SELECT id, item_name, quantity, unit, supply_date, notes, status, created_at
FROM supply_requests
WHERE supplier_id = %s AND status = 'Pending'
ORDER BY created_at DESC;
```

### 3.5 SELECT with BETWEEN — Range Queries
```sql
-- Batches by date range
SELECT pb.*, p.name AS product_name
FROM ProductionBatch pb
JOIN Product p ON p.product_id = pb.product_id
WHERE pb.production_date BETWEEN %s AND %s
ORDER BY pb.production_date, pb.batch_number;

-- Inventory by date range
SELECT i.inventory_date, p.name AS product_name, i.total_quantity,
       ROUND(i.total_quantity * p.unit_weight / 1000, 2) AS total_weight_kg
FROM Inventory i
JOIN Product p ON p.product_id = i.product_id
WHERE i.inventory_date BETWEEN %s AND %s
ORDER BY i.inventory_date;
```

### 3.6 SELECT with DATE() and CURDATE() — Date Functions
```sql
-- Today's supply requests only
SELECT id, item_name, quantity, unit, supply_date, notes, status, created_at
FROM supply_requests
WHERE supplier_id = %s AND DATE(created_at) = CURDATE()
ORDER BY created_at DESC;

-- Today's production output
SELECT COALESCE(SUM(quantity_produced), 0) AS s
FROM ProductionBatch
WHERE production_date = CURDATE();
```

### 3.7 Aggregate Functions — COUNT, SUM, COALESCE
```sql
-- Total suppliers
SELECT COUNT(*) AS cnt FROM Supplier;

-- Total raw materials
SELECT COUNT(*) AS cnt FROM RawMaterial;

-- Total batches
SELECT COUNT(*) AS cnt FROM ProductionBatch;

-- Grand total produced
SELECT COALESCE(SUM(total_quantity), 0) AS s FROM Inventory;

-- Today's production
SELECT COALESCE(SUM(quantity_produced), 0) AS s
FROM ProductionBatch WHERE production_date = CURDATE();

-- Low stock count
SELECT COUNT(*) AS cnt FROM RawMaterial WHERE quantity <= reorder_level;

-- Count other batches for same date (used in delete logic)
SELECT COUNT(*) AS cnt FROM ProductionBatch
WHERE product_id = %s AND production_date = %s AND batch_id != %s;
```

### 3.8 GROUP BY with Aggregate
```sql
-- Daily production totals (for chart)
SELECT production_date AS date, SUM(quantity_produced) AS total
FROM ProductionBatch
GROUP BY production_date
ORDER BY production_date;
```

### 3.9 Computed / Derived Columns with ROUND()
```sql
-- Inventory weight calculation
SELECT i.*, p.name AS product_name, p.unit_weight,
       ROUND(i.total_quantity * p.unit_weight / 1000, 2) AS total_weight_kg
FROM Inventory i
JOIN Product p ON p.product_id = i.product_id;
```

### 3.10 SELECT for Authentication (Login)
```sql
SELECT id, username, role, supplier_id
FROM users
WHERE username = %s AND password = %s;
```

---

## 4. TCL (Transaction Control Language)

### 4.1 COMMIT (used after every INSERT/UPDATE/DELETE)
```python
conn.commit()  # Called after every mutation query
```

### 4.2 Multi-statement Transaction (Delete batch with inventory adjustment)
```python
# Begin transaction (autocommit = False)
cur.execute("SELECT ...")          # Read batch info
cur.execute("SELECT COUNT(*)")     # Check sibling batches
cur.execute("DELETE FROM ..." )    # or UPDATE Inventory
cur.execute("DELETE FROM ProductionBatch ...")
conn.commit()                      # Commit all or nothing
```

---

## 5. Triggers (Procedural SQL)

### 5.1 AFTER INSERT Trigger — Auto-update Inventory + Deduct Raw Materials
```sql
CREATE TRIGGER after_batch_insert
AFTER INSERT ON ProductionBatch
FOR EACH ROW
BEGIN
    -- 1. Update Inventory (INSERT or UPDATE via ON DUPLICATE KEY)
    INSERT INTO Inventory (product_id, inventory_date, total_quantity)
    VALUES (NEW.product_id, NEW.production_date, NEW.quantity_produced)
    ON DUPLICATE KEY UPDATE
        total_quantity = total_quantity + NEW.quantity_produced;

    -- 2. Deduct raw materials based on recipe (UPDATE with JOIN)
    UPDATE RawMaterial rm
    JOIN ProductRecipe pr
        ON pr.material_id = rm.material_id
       AND pr.product_id  = NEW.product_id
    SET rm.quantity = GREATEST(0, rm.quantity - (NEW.quantity_produced * pr.qty_per_unit));
END;
```

### 5.2 AFTER UPDATE Trigger — Adjust Inventory + Compensate Raw Materials
```sql
CREATE TRIGGER after_batch_update
AFTER UPDATE ON ProductionBatch
FOR EACH ROW
BEGIN
    -- 1. Adjust Inventory
    UPDATE Inventory
    SET total_quantity = total_quantity - OLD.quantity_produced + NEW.quantity_produced
    WHERE product_id = NEW.product_id AND inventory_date = NEW.production_date;

    -- 2. Compensate raw material (add back OLD, subtract NEW)
    UPDATE RawMaterial rm
    JOIN ProductRecipe pr
        ON pr.material_id = rm.material_id
       AND pr.product_id  = NEW.product_id
    SET rm.quantity = GREATEST(0,
        rm.quantity
        + (OLD.quantity_produced * pr.qty_per_unit)
        - (NEW.quantity_produced * pr.qty_per_unit)
    );
END;
```

---

## 6. Built-in MySQL Functions Used

| Function | Purpose | Example |
|----------|---------|---------|
| `COUNT(*)` | Count rows | Total suppliers, batches, low stock |
| `SUM()` | Sum values | Total production, grand total inventory |
| `COALESCE()` | Handle NULL | `COALESCE(SUM(...), 0)` — return 0 instead of NULL |
| `GREATEST()` | Max of values | `GREATEST(0, qty - deduction)` — prevent negative stock |
| `ROUND()` | Round decimal | `ROUND(qty * weight / 1000, 2)` — weight in kg |
| `CURDATE()` | Current date | Filter today's batches/requests |
| `DATE()` | Extract date | `DATE(created_at) = CURDATE()` — match date from timestamp |
| `CURRENT_TIMESTAMP` | Current datetime | Default value for `created_at` column |

---

## 7. Constraints Summary

| Constraint | Where Used |
|-----------|-----------|
| `PRIMARY KEY` | All tables |
| `FOREIGN KEY` | RawMaterial → Supplier, ProductionBatch → Product, Inventory → Product, supply_requests → Supplier, ProductRecipe → Product & RawMaterial, users → Supplier |
| `UNIQUE KEY` | ProductionBatch (date+batch), Inventory (product+date), ProductRecipe (product+material), users (username) |
| `NOT NULL` | Most columns |
| `DEFAULT` | quantity=0, reorder_level=0, status='Pending', created_at=CURRENT_TIMESTAMP |
| `ENUM` | supply_requests.status, users.role |
| `ON DELETE CASCADE` | supply_requests, ProductRecipe, Supplier_Contact, Supplies |
| `ON DELETE SET NULL` | RawMaterial.supplier_id, users.supplier_id |
| `ON DELETE RESTRICT` | ProductionBatch, Inventory (prevent deleting products with data) |
| `ON UPDATE CASCADE` | All foreign keys |
| `AUTO_INCREMENT` | All primary key ID columns |

---

## 8. DBMS Concepts / Topics Covered

| # | Topic | Where Used |
|---|-------|-----------|
| 1 | **DDL** — CREATE DATABASE, CREATE TABLE, DROP TRIGGER, ALTER TABLE | `setup_db.py` |
| 2 | **DML** — INSERT, UPDATE, DELETE | All CRUD functions in `db.py` |
| 3 | **DQL** — SELECT with WHERE, JOIN, GROUP BY, ORDER BY | All query functions |
| 4 | **TCL** — COMMIT, Transaction handling | `run_mutation()`, `delete_production_batch()` |
| 5 | **Triggers** — AFTER INSERT, AFTER UPDATE | Auto inventory + raw material deduction |
| 6 | **INNER JOIN** | Batches↔Products, Recipe↔Materials, Requests↔Suppliers |
| 7 | **LEFT JOIN** | RawMaterial↔Supplier (supplier may be NULL) |
| 8 | **Aggregate Functions** | COUNT, SUM, COALESCE |
| 9 | **GROUP BY** | Daily production chart data |
| 10 | **BETWEEN** | Date range reports |
| 11 | **Date Functions** | CURDATE(), DATE(), CURRENT_TIMESTAMP |
| 12 | **UPSERT (ON DUPLICATE KEY UPDATE)** | Inventory auto-update, Recipe management |
| 13 | **ENUM data type** | Status (Pending/Approved/Rejected), Role (manager/supplier) |
| 14 | **Composite Primary Key** | Supplier_Contact, Supplies (M:N) |
| 15 | **Composite Unique Key** | ProductionBatch, Inventory, ProductRecipe |
| 16 | **Referential Integrity** | CASCADE, SET NULL, RESTRICT |
| 17 | **Parameterized Queries** | All queries use `%s` placeholders (SQL injection prevention) |
| 18 | **Multivalued Attribute** | Supplier_Contact table |
| 19 | **M:N Relationship** | Supplies table (Supplier ↔ RawMaterial) |
| 20 | **Computed Columns** | Weight calculation with ROUND() |
| 21 | **Conditional Logic** | GREATEST() to prevent negative values |
| 22 | **OLD / NEW references** | In triggers to access before/after values |
