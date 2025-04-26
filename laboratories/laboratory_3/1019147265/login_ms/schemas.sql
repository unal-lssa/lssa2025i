-- login_service/schemas.sql

CREATE DATABASE IF NOT EXISTS login_service;

USE login_service;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user'
);

-- Seed an admin user
INSERT IGNORE INTO users (username, password, role) 
VALUES ('admin', 'password123', 'admin');
VALUES ('test_user', 'password123', 'user');