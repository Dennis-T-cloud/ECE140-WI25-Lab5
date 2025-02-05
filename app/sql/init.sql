-- Create Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50),
    membership_level VARCHAR(20),
    join_date DATE
);

-- Create Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2),
    status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create Products table
CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

-- Create Order_Items table (for order details)
CREATE TABLE IF NOT EXISTS order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Add test data for customers
INSERT INTO customers (customer_id, name, email, city, membership_level, join_date)
VALUES 
(1, 'John Doe', 'john@example.com', 'New York', 'Gold', '2023-01-01'),
(2, 'Jane Smith', 'jane@example.com', 'Los Angeles', 'Silver', '2023-02-15'),
(3, 'Bob Johnson', 'bob@example.com', 'Chicago', 'Bronze', '2023-03-20'),
(4, 'Alice Brown', 'alice@example.com', 'Houston', 'Gold', '2023-04-10'),
(5, 'Charlie Wilson', 'charlie@example.com', 'Miami', 'Silver', '2023-05-05');

-- Add products
INSERT INTO products (product_id, name, category, price)
VALUES 
(1, 'Laptop', 'Electronics', 999.99),
(2, 'T-shirt', 'Clothing', 19.99),
(3, 'Novel', 'Books', 14.99),
(4, 'Garden Tools', 'Home & Garden', 49.99),
(5, 'Basketball', 'Sports', 29.99);

-- Add orders
INSERT INTO orders (order_id, customer_id, order_date, total_amount, status)
VALUES 
(1, 1, '2023-06-01', 1019.98, 'Completed'),
(2, 2, '2023-06-15', 64.98, 'Completed'),
(3, 3, '2023-07-01', 44.98, 'Processing'),
(4, 4, '2023-07-15', 1049.98, 'Shipped'),
(5, 5, '2023-08-01', 34.98, 'Completed');

-- Add order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES 
(1, 1, 1, 999.99),
(1, 2, 1, 19.99),
(2, 3, 1, 14.99),
(2, 4, 1, 49.99),
(3, 2, 1, 19.99),
(3, 3, 1, 14.99),
(4, 1, 1, 999.99),
(4, 4, 1, 49.99),
(5, 2, 1, 19.99),
(5, 5, 1, 14.99);