--  queries.sql  –  Analytical & date-based queries
--  Run with:  mysql -u root -p nutchoc_db < queries.sql

USE nutchoc_db;

-- Q1. Total Nut Chocolates produced per day
SELECT
    pb.production_date         AS "Date",
    SUM(pb.quantity_produced)  AS "Total Produced"
FROM ProductionBatch pb
GROUP BY pb.production_date
ORDER BY pb.production_date;

-- Q2. Total production across ALL days
SELECT SUM(quantity_produced) AS "Grand Total Produced"
FROM ProductionBatch;

-- Q3. Production batches for a specific date  (change the date as needed)
SELECT
    batch_id,
    batch_number,
    quantity_produced,
    notes
FROM ProductionBatch
WHERE production_date = '2026-03-11';

-- Q4. Inventory record for a specific date
SELECT
    i.inventory_date  AS "Date",
    p.name            AS "Product",
    i.total_quantity  AS "Total in Inventory"
FROM Inventory i
JOIN Product p ON p.product_id = i.product_id
WHERE i.inventory_date = '2026-03-11';

-- Q5. Production within a date range
SELECT
    pb.production_date,
    pb.batch_number,
    pb.quantity_produced,
    pb.notes
FROM ProductionBatch pb
WHERE pb.production_date BETWEEN '2026-03-10' AND '2026-03-12'
ORDER BY pb.production_date, pb.batch_number;

-- Q6. Raw material stock levels with supplier info  (JOIN)
SELECT
    rm.material_id,
    rm.name            AS "Material",
    rm.unit,
    rm.quantity        AS "In Stock",
    rm.reorder_level   AS "Reorder At",
    s.name             AS "Supplier",
    s.contact_phone    AS "Supplier Phone"
FROM RawMaterial rm
LEFT JOIN Supplier s ON s.supplier_id = rm.supplier_id
ORDER BY rm.name;

-- Q7. Materials below reorder level  (alert query)
SELECT
    rm.name          AS "Material",
    rm.quantity      AS "Current Stock",
    rm.reorder_level AS "Reorder Level",
    s.name           AS "Supplier"
FROM RawMaterial rm
LEFT JOIN Supplier s ON s.supplier_id = rm.supplier_id
WHERE rm.quantity <= rm.reorder_level;

-- Q8. Full inventory view with product name  (JOIN)
SELECT
    i.inventory_date         AS "Date",
    p.name                   AS "Product",
    p.unit_weight            AS "Weight/Piece (g)",
    i.total_quantity         AS "Total Pieces",
    (i.total_quantity * p.unit_weight / 1000) AS "Total Weight (kg)"
FROM Inventory i
JOIN Product p ON p.product_id = i.product_id
ORDER BY i.inventory_date;

-- Q9. Daily summary: batches + quantities
SELECT
    pb.production_date                          AS "Date",
    COUNT(pb.batch_id)                          AS "Batches Run",
    SUM(pb.quantity_produced)                   AS "Total Produced",
    MIN(pb.quantity_produced)                   AS "Min Batch Qty",
    MAX(pb.quantity_produced)                   AS "Max Batch Qty"
FROM ProductionBatch pb
GROUP BY pb.production_date
ORDER BY pb.production_date;
