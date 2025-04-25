-- Crear base de datos (opcional si se configura por entorno)
-- CREATE DATABASE myapp;

-- Seleccionar base de datos (solo necesario si el sistema lo requiere)
-- \c myapp;

-- Crear tabla de ejemplo
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) NOT NULL,
    doc_id VARCHAR(20) NOT NULL UNIQUE,
    doc_type VARCHAR(10) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    legal_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos iniciales
INSERT INTO users (role_name, doc_id, doc_type, first_name, last_name, legal_name) VALUES
('seller', '111111111', 'CC', 'Juan', 'Pérez', 'Juan'),
('buyer', '222222222', 'CC', 'María', 'Gómez', 'María Gómez'),
('admin', '333333333', 'CC', 'Carlos', 'López', 'Carlos López'),
('seller', '444444444', 'CC', 'Ana', 'Martínez', 'Ana Martínez'),
('buyer', '555555555', 'CC', 'Luis', 'Fernández', 'Luis Fernández');
