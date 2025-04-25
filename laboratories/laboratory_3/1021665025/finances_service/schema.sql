-- schema.sql for finances_db

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    type VARCHAR(50) NOT NULL -- e.g., 'income', 'expense'
);

-- Insert sample transactions
INSERT INTO transactions (description, amount, type) VALUES
('Rent Payment - Apt 101', 1500.00, 'income'),
('Utility Bill - Apt 101', -150.75, 'expense'),
('Rent Payment - Apt 203', 1250.00, 'income'),
('Maintenance - Apt 101 (Plumbing)', -300.00, 'expense'),
('Rent Payment - Apt 301', 1800.00, 'income'),
('Property Tax Payment', -2500.00, 'expense'),
('Cleaning Service - Apt 203', -85.00, 'expense');