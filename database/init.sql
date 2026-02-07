 Users  кестесі
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

 Rooms кестесі
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    room_number INT UNIQUE NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'Standard', 'Lux'
    price DECIMAL(10, 2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

Bookings кестесі
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    room_id INT REFERENCES rooms(id),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    total_price DECIMAL(10, 2)
);
