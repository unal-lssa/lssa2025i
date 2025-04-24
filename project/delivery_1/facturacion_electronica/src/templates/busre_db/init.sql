-- Crear base de datos (opcional si se configura por entorno)
-- CREATE DATABASE myapp;

-- Seleccionar base de datos (solo necesario si el sistema lo requiere)
-- \c myapp;

-- Crear tabla de ejemplo
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos iniciales
INSERT INTO users (username, email) VALUES
('alice', 'alice@example.com'),
('bob', 'bob@example.com');
