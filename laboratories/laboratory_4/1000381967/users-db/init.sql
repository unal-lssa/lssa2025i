CREATE TABLE if not exists users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);

INSERT INTO users (username, password, email) VALUES
('user1', 'password1', 'user1@unal.edu.co') 