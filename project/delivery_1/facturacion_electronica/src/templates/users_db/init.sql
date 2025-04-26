-- Crear base de datos (opcional si se configura por entorno)
-- CREATE DATABASE myapp;

-- Seleccionar base de datos (solo necesario si el sistema lo requiere)
-- \c myapp;

-- Crear tabla de ejemplo
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    role_name VARCHAR(20) NOT NULL,
    doc_id VARCHAR(20) NOT NULL
);

-- Insertar datos iniciales
INSERT INTO users (name, role_name, doc_id) VALUES
('Alice', 'admin', '123'),
('Bob', 'seller', '456'),
('Charlie', 'buyer', '789');