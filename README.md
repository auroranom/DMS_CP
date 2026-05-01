# 🍫 Nut Chocolate Production & Inventory Management System

A **DBMS Course Project** simulating a small-scale chocolate manufacturing unit using **MySQL** as the database backend and **Python Streamlit** as the frontend.

---

## Project Overview

| Feature | Details |
|---|---|
| Product | Nut Chocolate (single product) |
| Batches/Day | 2 (morning & evening) |
| Database | MySQL 8.x |
| Frontend | Python Streamlit |
| Charts | Plotly |

---

##  Database Schema

```
Supplier  ──<  RawMaterial
Product   ──<  ProductionBatch  ──triggers──>  Inventory
```

| Table | Description |
|---|---|
| `Supplier` | Raw material vendors |
| `RawMaterial` | Ingredients & packaging stock |
| `Product` | Nut Chocolate product record |
| `ProductionBatch` | Daily batch records (max 2/day) |
| `Inventory` | Auto-updated daily totals (via trigger) |

---

##  Setup Instructions

### 1. Prerequisites
- MySQL 8.x installed and running
- Python 3.9+ installed

### 2. Create the database & tables

Open **MySQL command line** or **MySQL Workbench**, then run:

```bash
mysql -u root -p < schema.sql
```

This creates the `nutchoc_db` database, all tables, and the triggers.

### 3. Load sample data

```bash
mysql -u root -p nutchoc_db < seed_data.sql
```

### 4. Configure your MySQL password

Open `db.py` and edit line 12:

```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "YOUR_PASSWORD_HERE",   # ← set your MySQL root password
    "database": "nutchoc_db",
}
```

### 5. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

---

## 📄 Project Files

| File | Purpose |
|---|---|
| `schema.sql` | DDL — all tables + 2 triggers |
| `seed_data.sql` | Sample suppliers, materials, batches |
| `queries.sql` | 9 analytical/date-based SQL queries |
| `db.py` | MySQL connection + all CRUD functions |
| `app.py` | Streamlit multi-page frontend |
| `requirements.txt` | Python package list |

---

##  Key DBMS Concepts Demonstrated

- **ER Modelling** → 5 entities with clear relationships
- **Normalization** → All tables in 3NF
- **Primary & Foreign Keys** → Enforced referential integrity
- **Triggers** → `after_batch_insert` auto-updates `Inventory`
- **Joins** → Used in all reporting queries
- **Date-based Queries** → Filter by date / date range
- **CRUD Operations** → Full create/read/update/delete via UI
- **Aggregate Functions** → SUM, COUNT, MIN, MAX in reports
- **DB–UI Integration** → Streamlit frontend talks live to MySQL

---

## 🖥️ Application Pages

| Page | Description |
|---|---|
|  Dashboard | KPI cards + daily production chart + low-stock alerts |
|  Supplier Management | Add, edit, delete suppliers |
|  Raw Material Management | Track & update ingredient stock |
|  Production Batches | Record/edit the two daily batches |
|  Inventory Monitoring | View auto-updated daily totals |
|  Reports | Date-range reports + analytics charts |

---

##  Trigger Explanation

```sql
AFTER INSERT ON ProductionBatch
→ INSERT INTO Inventory ... ON DUPLICATE KEY UPDATE total_quantity += NEW.quantity_produced
```

When a production batch row is inserted, the trigger **automatically upserts** the corresponding `Inventory` row for that date — no manual step required.
