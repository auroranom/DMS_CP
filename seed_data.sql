
--  seed_data.sql  –  Sample / demo data

USE nutchoc_db;

-- Suppliers
INSERT INTO Supplier (name, contact_phone, email, address) VALUES
('ChocoCraft Suppliers',  '9876543210', 'chococraft@example.com',  '12 Cocoa Lane, Mumbai'),
('NutriNuts Pvt. Ltd.',   '9123456780', 'nutrinuts@example.com',   '45 Almond Street, Pune'),
('SweetPack Industries',  '9988776655', 'sweetpack@example.com',   '8 Sugar Park, Nashik');

-- Raw Materials (Typical Nut Chocolate ingredients)
INSERT INTO RawMaterial (name, unit, quantity, reorder_level, supplier_id) VALUES
('Compound Chocolate',  'kg',  250.00, 50.00, 1),
('Cocoa Powder',        'kg',  120.00, 30.00, 1),
('Sugar',               'kg',  300.00, 60.00, 3),
('Milk Powder',         'kg',  180.00, 40.00, 3),
('Crushed Cashew Nuts', 'kg',  100.00, 25.00, 2),
('Roasted Almonds',     'kg',   80.00, 20.00, 2),
('Aluminium Foil',      'pcs', 5000.00, 500.00, 3),
('Cardboard Boxes',     'pcs', 2000.00, 200.00, 3);

-- Product
INSERT INTO Product (name, description, unit_weight) VALUES
('Nut Chocolate',
 'Premium milk chocolate bar enriched with crushed cashews and roasted almonds.',
 50.00);
 
-- Supplier Contacts (multivalued)
INSERT INTO Supplier_Contact (supplier_id, contact_no) VALUES
(1, '9877543443'),
(1, '9045637287'),
(2, '9132453456'),
(3, '9945344658'),
(3, '9074663407');

-- Supplies (Supplier ↔ RawMaterial)
INSERT INTO Supplies (supplier_id, material_id) VALUES
(1,1),(1,2),
(3,3),(3,4),
(2,5),(2,6),
(3,7),(3,8);

-- Production Batches (3 days × 2 batches)
-- Trigger will auto-populate Inventory
INSERT INTO ProductionBatch (product_id, production_date, batch_number, quantity_produced, notes) VALUES
(1, '2026-03-10', 1, 500, 'Morning batch – machine A'),
(1, '2026-03-10', 2, 480, 'Evening batch – machine B'),
(1, '2026-03-11', 1, 520, 'Morning batch – machine A'),
(1, '2026-03-11', 2, 510, 'Evening batch – machine B'),
(1, '2026-03-12', 1, 490, 'Morning batch – production as usual'),
(1, '2026-03-12', 2, 505, 'Evening batch – slight delay');

