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
    pwd VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos iniciales
INSERT INTO users (role_name, doc_id, doc_type, first_name, last_name, legal_name, pwd) VALUES
('admin', '000000', 'CC', 'Sebaxtian', 'Bach', 'TI', 'e10adc3949ba59abbe56e057f20f883e'),
('seller', '111111', 'NIT', 'Vendedor', 'Uno', 'S.A.S', 'e10adc3949ba59abbe56e057f20f883e'),
('buyer', '222222', 'CC', 'Comprador', 'Uno', 'NA', 'e10adc3949ba59abbe56e057f20f883e');
