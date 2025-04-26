CREATE DATABASE IF NOT EXISTS appsettings_service;

USE appsettings_service;

CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    value TEXT NOT NULL
);
