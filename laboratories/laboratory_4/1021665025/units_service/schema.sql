-- schema.sql for units_db

CREATE TABLE IF NOT EXISTS rental_units (
    id SERIAL PRIMARY KEY,
    unit_number VARCHAR(50) UNIQUE NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(20),
    bedrooms INTEGER,
    bathrooms DECIMAL(3, 1),
    rent_amount DECIMAL(10, 2) NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample rental units
INSERT INTO rental_units (unit_number, address, city, state, zip_code, bedrooms, bathrooms, rent_amount, is_available, description) VALUES
('101', '123 Main St', 'Austin', 'TX', '78701', 2, 1.5, 1500.00, FALSE, 'Spacious 2 bedroom apartment.'),
('203', '456 Oak Ave', 'Dallas', 'TX', '75201', 1, 1.0, 1250.00, TRUE, 'Cozy 1 bedroom with downtown views.'),
('301', '789 Pine Ln', 'Houston', 'TX', '77001', 3, 2.0, 1800.00, TRUE, 'Large 3 bedroom house with backyard.'),
('4A', '1011 Broadway', 'San Antonio', 'TX', '78205', 2, 2.0, 1600.00, TRUE, 'Modern apartment in the city center.');