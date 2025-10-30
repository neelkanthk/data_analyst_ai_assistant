-- E-commerce Database Schema and Dummy Data
-- Drop existing tables if needed
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS addresses CASCADE;

-- Create Tables

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    cost_price NUMERIC(10,2) NOT NULL,
    sku VARCHAR(50) UNIQUE,
    weight_kg NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    quantity_available INTEGER NOT NULL,
    quantity_reserved INTEGER DEFAULT 0,
    warehouse_location VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15),
    date_of_birth DATE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    address_type VARCHAR(20),
    street_address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(10) NOT NULL,
    country VARCHAR(50) DEFAULT 'India',
    is_default BOOLEAN DEFAULT FALSE
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TIMESTAMP NOT NULL,
    shipping_address_id INTEGER REFERENCES addresses(address_id),
    order_status VARCHAR(30) NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    discount_amount NUMERIC(10,2) DEFAULT 0,
    shipping_cost NUMERIC(10,2) DEFAULT 0,
    payment_method VARCHAR(30),
    payment_status VARCHAR(20),
    delivery_date DATE
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    discount NUMERIC(10,2) DEFAULT 0,
    subtotal NUMERIC(10,2) NOT NULL
);

CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    customer_id INTEGER REFERENCES customers(customer_id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Categories
INSERT INTO categories (category_name, description) VALUES
('Electronics', 'Electronic gadgets and accessories'),
('Clothing', 'Apparel and fashion items'),
('Home & Kitchen', 'Home essentials and kitchen items'),
('Beauty & Personal Care', 'Cosmetics and personal care products'),
('Sports & Fitness', 'Sports equipment and fitness accessories');

-- Insert 10 Products
INSERT INTO products (category_id, product_name, description, price, cost_price, sku, weight_kg) VALUES
(1, 'Wireless Bluetooth Earbuds', 'Premium noise-cancelling earbuds with 24hr battery', 2999.00, 1500.00, 'ELEC-WBE-001', 0.15),
(1, 'Smart Watch Pro', 'Fitness tracker with heart rate monitor and GPS', 8999.00, 4500.00, 'ELEC-SWP-002', 0.25),
(2, 'Cotton Casual T-Shirt', 'Comfortable round neck t-shirt in multiple colors', 599.00, 250.00, 'CLTH-CCT-003', 0.20),
(2, 'Denim Jeans', 'Slim fit denim jeans for men', 1499.00, 700.00, 'CLTH-DNJ-004', 0.50),
(3, 'Stainless Steel Water Bottle', '1 liter insulated water bottle', 799.00, 350.00, 'HOME-SWB-005', 0.40),
(3, 'Non-Stick Cookware Set', '5-piece non-stick cooking set', 3499.00, 1800.00, 'HOME-NCW-006', 3.50),
(4, 'Face Serum with Vitamin C', 'Anti-aging serum for glowing skin', 1299.00, 550.00, 'BEAU-FSV-007', 0.10),
(4, 'Natural Hair Oil', 'Herbal hair growth oil 200ml', 449.00, 180.00, 'BEAU-NHO-008', 0.22),
(5, 'Yoga Mat Premium', 'Extra thick exercise mat with carrying strap', 1899.00, 900.00, 'SPRT-YMP-009', 1.20),
(5, 'Resistance Bands Set', 'Set of 5 resistance bands for strength training', 999.00, 450.00, 'SPRT-RBS-010', 0.35);

-- Insert Inventory
INSERT INTO inventory (product_id, quantity_available, quantity_reserved, warehouse_location) VALUES
(1, 150, 10, 'Mumbai Warehouse A'),
(2, 80, 5, 'Mumbai Warehouse A'),
(3, 500, 25, 'Delhi Warehouse B'),
(4, 200, 15, 'Delhi Warehouse B'),
(5, 300, 20, 'Bangalore Warehouse C'),
(6, 120, 8, 'Bangalore Warehouse C'),
(7, 250, 18, 'Mumbai Warehouse A'),
(8, 400, 30, 'Delhi Warehouse B'),
(9, 180, 12, 'Bangalore Warehouse C'),
(10, 350, 22, 'Mumbai Warehouse A');

-- Insert 50 Customers
INSERT INTO customers (first_name, last_name, email, phone, date_of_birth, registration_date, customer_status)
SELECT 
    first_names[floor(random() * 20 + 1)],
    last_names[floor(random() * 20 + 1)],
    'customer' || s || '@email.com',
    '9' || lpad((floor(random() * 900000000 + 100000000))::text, 9, '0'),
    DATE '1975-01-01' + (random() * 15000)::integer,
    TIMESTAMP '2022-01-01' + (random() * interval '1095 days'),
    CASE WHEN random() < 0.95 THEN 'Active' ELSE 'Inactive' END
FROM generate_series(1, 50) s,
(SELECT ARRAY['Raj', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Ananya', 'Rohan', 'Kavya', 'Arjun', 'Meera',
              'Sanjay', 'Pooja', 'Karan', 'Riya', 'Aditya', 'Nisha', 'Rahul', 'Divya', 'Manish', 'Shreya'] as first_names,
       ARRAY['Sharma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Gupta', 'Joshi', 'Verma', 'Agarwal', 'Iyer',
              'Mehta', 'Shah', 'Nair', 'Desai', 'Kapoor', 'Malhotra', 'Rao', 'Chopra', 'Bhat', 'Menon'] as last_names) names;

-- Insert Addresses (1-2 addresses per customer)
INSERT INTO addresses (customer_id, address_type, street_address, city, state, postal_code, is_default)
SELECT 
    c.customer_id,
    CASE WHEN random() < 0.7 THEN 'Home' ELSE 'Office' END,
    (floor(random() * 999 + 1))::text || ', ' || 
    (ARRAY['MG Road', 'Park Street', 'Mall Road', 'Gandhi Nagar', 'Station Road', 'Main Street'])[floor(random() * 6 + 1)],
    (ARRAY['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Jaipur'])[floor(random() * 8 + 1)],
    (ARRAY['Maharashtra', 'Delhi', 'Karnataka', 'Telangana', 'Tamil Nadu', 'West Bengal', 'Maharashtra', 'Rajasthan'])[floor(random() * 8 + 1)],
    lpad((floor(random() * 900000 + 100000))::text, 6, '0'),
    TRUE
FROM customers c;

-- Insert Orders (200 orders across 2022-2024)
WITH order_data AS (
    SELECT 
        (floor(random() * 50 + 1))::integer as customer_id,
        TIMESTAMP '2022-01-01' + (random() * interval '1095 days') as order_date,
        (ARRAY['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'])[
            CASE 
                WHEN random() < 0.05 THEN 5
                WHEN random() < 0.10 THEN 1
                WHEN random() < 0.20 THEN 2
                WHEN random() < 0.40 THEN 3
                ELSE 4
            END
        ] as order_status,
        (ARRAY['Card', 'UPI', 'Net Banking', 'Cash on Delivery', 'Wallet'])[floor(random() * 5 + 1)] as payment_method,
        generate_series as order_num
    FROM generate_series(1, 200)
)
INSERT INTO orders (customer_id, order_date, shipping_address_id, order_status, total_amount, discount_amount, shipping_cost, payment_method, payment_status, delivery_date)
SELECT 
    od.customer_id,
    od.order_date,
    a.address_id,
    od.order_status,
    0, -- will update after order_items
    CASE WHEN random() < 0.3 THEN (random() * 500)::numeric(10,2) ELSE 0 END,
    CASE 
        WHEN random() < 0.4 THEN 0 
        WHEN random() < 0.8 THEN 50 
        ELSE 100 
    END,
    od.payment_method,
    CASE 
        WHEN od.order_status = 'Cancelled' THEN 'Refunded'
        WHEN od.order_status IN ('Delivered', 'Shipped') THEN 'Paid'
        WHEN od.order_status = 'Processing' THEN 'Paid'
        ELSE 'Pending'
    END,
    CASE 
        WHEN od.order_status = 'Delivered' THEN (od.order_date + interval '3 days' + (random() * interval '7 days'))::date
        ELSE NULL
    END
FROM order_data od
JOIN addresses a ON a.customer_id = od.customer_id AND a.is_default = TRUE;

-- Insert Order Items (1-4 items per order)
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount, subtotal)
SELECT 
    o.order_id,
    (floor(random() * 10 + 1))::integer as product_id,
    (floor(random() * 3 + 1))::integer as quantity,
    p.price,
    CASE WHEN random() < 0.2 THEN (p.price * 0.1 * (floor(random() * 3 + 1)))::numeric(10,2) ELSE 0 END,
    0 -- will calculate
FROM orders o
CROSS JOIN LATERAL (
    SELECT generate_series(1, (floor(random() * 4 + 1))::integer)
) items
JOIN products p ON p.product_id = (floor(random() * 10 + 1))::integer;

-- Update subtotal for order_items
UPDATE order_items
SET subtotal = (quantity * unit_price) - discount;

-- Update total_amount for orders
UPDATE orders o
SET total_amount = (
    SELECT COALESCE(SUM(oi.subtotal), 0) + o.shipping_cost - o.discount_amount
    FROM order_items oi
    WHERE oi.order_id = o.order_id
);

-- Insert Reviews (150 reviews from customers who placed orders)
INSERT INTO reviews (product_id, customer_id, rating, review_text, review_date)
SELECT 
    oi.product_id,
    o.customer_id,
    (floor(random() * 3 + 3))::integer, -- ratings between 3-5
    (ARRAY[
        'Great product! Highly recommended.',
        'Good quality and fast delivery.',
        'Value for money. Very satisfied.',
        'Excellent product, will buy again.',
        'Nice quality, meets expectations.',
        'Awesome! Loved it.',
        'Good purchase, happy with the product.',
        'Satisfied with the quality and price.',
        'Decent product for the price.',
        'Meets my requirements perfectly.'
    ])[floor(random() * 10 + 1)],
    o.order_date + (random() * interval '30 days')
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered' AND random() < 0.4
LIMIT 150;

-- Summary Statistics
SELECT 'Database Summary' as info, '---' as value
UNION ALL
SELECT 'Total Products', COUNT(*)::text FROM products
UNION ALL
SELECT 'Total Customers', COUNT(*)::text FROM customers
UNION ALL
SELECT 'Total Orders', COUNT(*)::text FROM orders
UNION ALL
SELECT 'Total Order Items', COUNT(*)::text FROM order_items
UNION ALL
SELECT 'Total Reviews', COUNT(*)::text FROM reviews
UNION ALL
SELECT 'Delivered Orders', COUNT(*)::text FROM orders WHERE order_status = 'Delivered'
UNION ALL
SELECT 'Pending Orders', COUNT(*)::text FROM orders WHERE order_status = 'Pending'
UNION ALL
SELECT 'Total Revenue', TO_CHAR(SUM(total_amount), '₹99,99,999.99') FROM orders WHERE order_status = 'Delivered';