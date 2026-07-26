```sql
-- Create Database
CREATE DATABASE IF NOT EXISTS healthcare;
USE healthcare;

-- Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    age INT,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Doctors Table
CREATE TABLE doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

INSERT IGNORE INTO doctors (doctor_name, specialization, email, password_hash) VALUES
('Dr. Rajesh Kumar', 'Cardiologist', 'rajesh.cardiology@example.com', 'doctor123'),
('Dr. Priya Sharma', 'Diabetologist', 'priya.diabetes@example.com', 'doctor123'),
('Dr. Anil Reddy', 'Orthopedic', 'anil.ortho@example.com', 'doctor123'),
('Dr. Sneha Patel', 'Physiotherapist', 'sneha.physio@example.com', 'doctor123');

-- Admins Table
CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Disease Predictions
CREATE TABLE predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    disease VARCHAR(100),
    probability FLOAT,
    result VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Appointments
CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    doctor_id INT,
    appointment_date DATE,
    status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- AI Chat History
CREATE TABLE chatbot_history (
    chat_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    question TEXT,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Diet Plans
CREATE TABLE diet_plans (
    diet_id INT AUTO_INCREMENT PRIMARY KEY,
    disease VARCHAR(100),
    food_name VARCHAR(100),
    meal_type VARCHAR(50)
);

-- Physiotherapy Plans
CREATE TABLE physiotherapy_plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    disease VARCHAR(100),
    exercise_name VARCHAR(100),
    duration VARCHAR(50)
);

-- Doctor Recommendations
CREATE TABLE doctor_recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    doctor_id INT,
    suggestion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- Feedback
CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    rating INT,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```
