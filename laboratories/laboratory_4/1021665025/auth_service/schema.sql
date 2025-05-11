-- schema.sql for auth_db

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
);

-- Create the roles table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL
);

-- Create a linking table for the many-to-many relationship between users and roles
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);

-- Insert initial roles
INSERT INTO roles (name) VALUES ('user') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('admin') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('super_admin') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('finance') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('legal') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('finance_assistance') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name) VALUES ('legal_assitance') ON CONFLICT (name) DO NOTHING;

-- Insert test users with hashed passwords (using 'password123' for simplicity in testing)
-- These hashes were generated using bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())

-- User with 'user' role
INSERT INTO users (username, password_hash) VALUES ('test_user', '$2b$12$xDRA1G0zAHyay45CnmNWYuWa/VXUHgy2GLycJlt1sXu3241lM8bTy') ON CONFLICT (username) DO NOTHING;

-- User with 'admin' role
INSERT INTO users (username, password_hash) VALUES ('test_admin', '$2b$12$xDRA1G0zAHyay45CnmNWYuWa/VXUHgy2GLycJlt1sXu3241lM8bTy') ON CONFLICT (username) DO NOTHING;

-- User with 'super_admin' role
INSERT INTO users (username, password_hash) VALUES ('test_superadmin', '$2b$12$xDRA1G0zAHyay45CnmNWYuWa/VXUHgy2GLycJlt1sXu3241lM8bTy') ON CONFLICT (username) DO NOTHING;

-- User with 'finance' role
INSERT INTO users (username, password_hash) VALUES ('test_finance', '$2b$12$xDRA1G0zAHyay45CnmNWYuWa/VXUHgy2GLycJlt1sXu3241lM8bTy') ON CONFLICT (username) DO NOTHING;

-- User with 'legal' role
INSERT INTO users (username, password_hash) VALUES ('test_legal', '$2b$12$xDRA1G0zAHyay45CnmNWYuWa/VXUHgy2GLycJlt1sXu3241lM8bTy') ON CONFLICT (username) DO NOTHING;

-- User with 'finance_assistance' role
INSERT INTO users (username, password_hash) VALUES ('test_finance_assist', '$2b$12$xDRA1G0zAHyay45CnmNWYuWa/VXUHgy2GLycJlt1sXu3241lM8bTy') ON CONFLICT (username) DO NOTHING;

-- User with 'legal_assitance' role
INSERT INTO users (username, password_hash) VALUES ('test_legal_assist', '$2b$12$xDRA1G0zAHyay45CnmNWYuWa/VXUHgy2GLycJlt1sXu3241lM8bTy') ON CONFLICT (username) DO NOTHING;

-- A user with multiple roles (admin + finance)
INSERT INTO users (username, password_hash) VALUES ('test_multifunction', '$2b$12$xDRA1G0zAHyay45CnmNWYuWa/VXUHgy2GLycJlt1sXu3241lM8bTy') ON CONFLICT (username) DO NOTHING;


-- Assign roles to the test users
-- Assign 'user' role to test_user
INSERT INTO user_roles (user_id, role_id) VALUES (
    (SELECT id FROM users WHERE username = 'test_user'),
    (SELECT id FROM roles WHERE name = 'user')
) ON CONFLICT DO NOTHING;

-- Assign 'admin' role to test_admin
INSERT INTO user_roles (user_id, role_id) VALUES (
    (SELECT id FROM users WHERE username = 'test_admin'),
    (SELECT id FROM roles WHERE name = 'admin')
) ON CONFLICT DO NOTHING;

-- Assign 'super_admin' role to test_superadmin
INSERT INTO user_roles (user_id, role_id) VALUES (
    (SELECT id FROM users WHERE username = 'test_superadmin'),
    (SELECT id FROM roles WHERE name = 'super_admin')
) ON CONFLICT DO NOTHING;

-- Assign 'finance' role to test_finance
INSERT INTO user_roles (user_id, role_id) VALUES (
    (SELECT id FROM users WHERE username = 'test_finance'),
    (SELECT id FROM roles WHERE name = 'finance')
) ON CONFLICT DO NOTHING;

-- Assign 'legal' role to test_legal
INSERT INTO user_roles (user_id, role_id) VALUES (
    (SELECT id FROM users WHERE username = 'test_legal'),
    (SELECT id FROM roles WHERE name = 'legal')
) ON CONFLICT DO NOTHING;

-- Assign 'finance_assistance' role to test_finance_assist
INSERT INTO user_roles (user_id, role_id) VALUES (
    (SELECT id FROM users WHERE username = 'test_finance_assist'),
    (SELECT id FROM roles WHERE name = 'finance_assistance')
) ON CONFLICT DO NOTHING;

-- Assign 'legal_assitance' role to test_legal_assist
INSERT INTO user_roles (user_id, role_id) VALUES (
    (SELECT id FROM users WHERE username = 'test_legal_assist'),
    (SELECT id FROM roles WHERE name = 'legal_assitance')
) ON CONFLICT DO NOTHING;

-- Assign multiple roles to test_multifunction (e.g., admin and finance)
INSERT INTO user_roles (user_id, role_id) VALUES (
    (SELECT id FROM users WHERE username = 'test_multifunction'),
    (SELECT id FROM roles WHERE name = 'admin')
) ON CONFLICT DO NOTHING;
INSERT INTO user_roles (user_id, role_id) VALUES (
    (SELECT id FROM users WHERE username = 'test_multifunction'),
    (SELECT id FROM roles WHERE name = 'finance')
) ON CONFLICT DO NOTHING;