CREATE TABLE tutors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    subject VARCHAR(100),
    rating FLOAT
);

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    tutor_id INT REFERENCES tutors(id),
    time TIMESTAMP
);

INSERT INTO tutors (name, subject, rating) VALUES
('Alice', 'Math', 4.9),
('Bob', 'Science', 4.7);

INSERT INTO students (name) VALUES
('John Doe'),
('Jane Smith');

