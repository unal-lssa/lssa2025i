CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

INSERT INTO products (name, price) VALUES
('Frutino', 2000),
('Quipitos', 1500),
('Vive100', 3000),
('Nutribela', 25000);