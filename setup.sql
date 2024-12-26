DROP SCHEMA IF EXISTS revive_system;
CREATE SCHEMA revive_system;
USE revive_system;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE
);

-- Create item_types table
CREATE TABLE item_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    attributes TEXT NOT NULL 
    -- attributes 存储以 JSON 格式定义的动态属性
);

-- Create items table
CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    type_id INT NOT NULL,
    created_by INT,
    FOREIGN KEY (type_id) REFERENCES item_types(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create electronics attributes table
CREATE TABLE electronics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    brand VARCHAR(50),
    warranty_period INT,
    state VARCHAR(50),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- Create furniture attributes table
CREATE TABLE furniture (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    material VARCHAR(50),
    dimensions VARCHAR(100),
    weight INT,
    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- Create clothing attributes table
CREATE TABLE clothing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    size VARCHAR(20),
    color VARCHAR(20),
    material VARCHAR(50),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- -- Create approvals table
-- CREATE TABLE approvals (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     user_id INT NOT NULL,
--     admin_id INT,
--     approved BOOLEAN,
--     approval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (user_id) REFERENCES users(id),
--     FOREIGN KEY (admin_id) REFERENCES users(id)
-- );

-- Initialize data for users table
INSERT INTO users (username, password, email, phone, address, is_admin, is_approved)
VALUES 
('admin', 'admin123', 'admin@example.com', '1234567890', '123 Admin Street', TRUE, TRUE),
('user1', 'user123', 'user1@example.com', '9876543210', '456 User Lane', FALSE, TRUE),
('user2', 'user456', 'user2@example.com', '6543219870', '789 User Avenue', FALSE, FALSE);

-- 初始化物品类型表
INSERT INTO item_types (name, attributes)
VALUES 
('Electronics', '{"brand": "string", "warranty_period": "int", "state": "string"}'),
('Furniture', '{"material": "string", "dimensions": "string", "weight": "int"}'),
('Clothing', '{"size": "string", "color": "string", "material": "string"}');

-- Initialize data for items table
INSERT INTO items (name, description, address, phone, email, type_id, created_by)
VALUES 
('Laptop', 'A high-performance laptop', '123 Tech Blvd', '1234567890', 'seller1@example.com', 1, 2),
('Sofa', 'A comfortable three-seater sofa', '456 Furniture Ave', '9876543210', 'seller2@example.com', 2, 2),
('Jacket', 'A stylish leather jacket', '789 Clothing Lane', '6543219870', 'seller3@example.com', 3, 2);

-- Initialize data for electronics attributes
INSERT INTO electronics (item_id, brand, warranty_period, state)
VALUES 
(1, 'TechBrand', 24, 'New');

-- Initialize data for furniture attributes
INSERT INTO furniture (item_id, material, dimensions, weight)
VALUES 
(2, 'Leather', '200x100x90', 30);

-- Initialize data for clothing attributes
INSERT INTO clothing (item_id, size, color, material)
VALUES 
(3, 'L', 'Black', 'Leather');

-- -- Initialize data for approvals table
-- INSERT INTO approvals (user_id, admin_id, approved)
-- VALUES 
-- (2, 1, TRUE),
-- (3, 1, FALSE);
