
--  Nut Chocolate Production & Inventory Management System
--  schema.sql  –  DDL + Trigger

CREATE DATABASE IF NOT EXISTS nutchoc_db;
USE nutchoc_db;


-- 1. Supplier
CREATE TABLE IF NOT EXISTS Supplier (
    supplier_id   INT          NOT NULL AUTO_INCREMENT,
    name          VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(15),
    email         VARCHAR(100),
    address       VARCHAR(255),
    PRIMARY KEY (supplier_id)
);

-- 2. RawMaterial ( Represents every ingredient / packaging component)
CREATE TABLE IF NOT EXISTS RawMaterial (
    material_id   INT          NOT NULL AUTO_INCREMENT,
    name          VARCHAR(100) NOT NULL,
    unit          VARCHAR(20)  NOT NULL,          -- kg / g / litre / pcs
    quantity      DECIMAL(10,2) NOT NULL DEFAULT 0,
    reorder_level DECIMAL(10,2) NOT NULL DEFAULT 0,
    supplier_id   INT,
    PRIMARY KEY (material_id),
    CONSTRAINT fk_rm_supplier
        FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- 3. Product (Only one product: Nut Chocolate)
CREATE TABLE IF NOT EXISTS Product (
    product_id  INT          NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    unit_weight DECIMAL(6,2) NOT NULL DEFAULT 0,  -- weight per piece (g)
    PRIMARY KEY (product_id)
);

-- 5. Inventory (One row per day; total is maintained by trigger)
CREATE TABLE IF NOT EXISTS Inventory (
    inventory_id    INT  NOT NULL AUTO_INCREMENT,
    product_id      INT  NOT NULL,
    inventory_date  DATE NOT NULL,
    total_quantity  INT  NOT NULL DEFAULT 0,
    PRIMARY KEY (inventory_id),
    UNIQUE KEY uq_inv_date (product_id, inventory_date),
    CONSTRAINT fk_inv_product
        FOREIGN KEY (product_id) REFERENCES Product(product_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 6. ProductionBatch (Two batches per day (batch_number IN (1,2)))
CREATE TABLE IF NOT EXISTS ProductionBatch (
    batch_id          INT  NOT NULL AUTO_INCREMENT,
    product_id        INT  NOT NULL,
    production_date   DATE NOT NULL,
    batch_number      TINYINT NOT NULL CHECK (batch_number IN (1, 2)),
    quantity_produced INT  NOT NULL DEFAULT 0,     -- number of chocolates
    notes             VARCHAR(255),
    PRIMARY KEY (batch_id),
    UNIQUE KEY uq_date_batch (production_date, batch_number),
    CONSTRAINT fk_pb_product
        FOREIGN KEY (product_id) REFERENCES Product(product_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 7. Supplier_Contact (multivalued attribute)
CREATE TABLE IF NOT EXISTS Supplier_Contact (
    supplier_id INT,
    contact_no VARCHAR(15),
    PRIMARY KEY (supplier_id, contact_no),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- 8. Supplies (Supplier ↔ RawMaterial)  M:N
CREATE TABLE IF NOT EXISTS Supplies (
    supplier_id INT,
    material_id INT,
    PRIMARY KEY (supplier_id, material_id),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (material_id) REFERENCES RawMaterial(material_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

