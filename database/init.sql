-- ============================================================
--  Infinity-Void Hotel Management System
--  Database Schema v2.0
--  Author: Ahrar (anarbaevahrar01-wq)
--  Description: Full relational schema with constraints,
--               indexes, triggers and seed data
-- ============================================================

-- Drop tables if exist (for clean re-run)
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS room_categories;
DROP TABLE IF EXISTS audit_log;

-- ============================================================
--  TABLE: room_categories
--  Stores room type definitions and descriptions
-- ============================================================
CREATE TABLE room_categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL UNIQUE,
    description TEXT,
    base_price  DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
--  TABLE: users
--  Stores registered hotel system users
--  password_hash: bcrypt hash, never store plain text
-- ============================================================
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'guest',
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT users_username_length CHECK (char_length(username) >= 2),
    CONSTRAINT users_email_format    CHECK (email LIKE '%@%'),
    CONSTRAINT users_role_valid      CHECK (role IN ('guest', 'admin', 'staff'))
);

-- ============================================================
--  TABLE: rooms
--  Stores hotel room inventory
-- ============================================================
CREATE TABLE rooms (
    id           SERIAL PRIMARY KEY,
    room_number  INTEGER      NOT NULL UNIQUE,
    type         VARCHAR(20)  NOT NULL,
    floor        INTEGER      NOT NULL DEFAULT 1,
    capacity     INTEGER      NOT NULL DEFAULT 2,
    price        DECIMAL(10,2) NOT NULL,
    is_available BOOLEAN      NOT NULL DEFAULT TRUE,
    description  TEXT,
    created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT rooms_number_positive  CHECK (room_number > 0),
    CONSTRAINT rooms_price_positive   CHECK (price > 0),
    CONSTRAINT rooms_capacity_valid   CHECK (capacity BETWEEN 1 AND 10),
    CONSTRAINT rooms_floor_valid      CHECK (floor BETWEEN 1 AND 50),
    CONSTRAINT rooms_type_valid       CHECK (type IN ('Standard', 'Lux'))
);

-- ============================================================
--  TABLE: bookings
--  Stores reservation records (One-to-Many: user, room)
-- ============================================================
CREATE TABLE bookings (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER      NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    room_id     INTEGER      NOT NULL REFERENCES rooms(id)  ON DELETE RESTRICT,
    check_in    DATE         NOT NULL,
    check_out   DATE         NOT NULL,
    total_price DECIMAL(10,2),
    status      VARCHAR(20)  NOT NULL DEFAULT 'confirmed',
    notes       TEXT,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT bookings_dates_valid   CHECK (check_out > check_in),
    CONSTRAINT bookings_status_valid  CHECK (status IN ('confirmed', 'cancelled', 'completed'))
);

-- ============================================================
--  TABLE: audit_log
--  Tracks important system events
-- ============================================================
CREATE TABLE audit_log (
    id         SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    action     VARCHAR(10) NOT NULL,
    row_id     INTEGER,
    changed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details    TEXT,

    CONSTRAINT audit_action_valid CHECK (action IN ('INSERT', 'UPDATE', 'DELETE'))
);

-- ============================================================
--  INDEXES — speeds up frequent queries
-- ============================================================
CREATE INDEX idx_users_email        ON users(email);
CREATE INDEX idx_users_role         ON users(role);
CREATE INDEX idx_rooms_type         ON rooms(type);
CREATE INDEX idx_rooms_available    ON rooms(is_available);
CREATE INDEX idx_rooms_floor        ON rooms(floor);
CREATE INDEX idx_bookings_user      ON bookings(user_id);
CREATE INDEX idx_bookings_room      ON bookings(room_id);
CREATE INDEX idx_bookings_checkin   ON bookings(check_in);
CREATE INDEX idx_bookings_checkout  ON bookings(check_out);
CREATE INDEX idx_bookings_status    ON bookings(status);
CREATE INDEX idx_audit_table        ON audit_log(table_name);
CREATE INDEX idx_audit_changed_at   ON audit_log(changed_at);

-- ============================================================
--  SEED DATA — room_categories
-- ============================================================
INSERT INTO room_categories (name, description, base_price) VALUES
    ('Standard', 'Comfortable standard room with all basic amenities', 5000.00),
    ('Lux',      'Luxury suite with premium furnishings and city view', 15000.00);

-- ============================================================
--  SEED DATA — users (passwords are bcrypt hashed)
--  plain: admin123   → hash below
--  plain: guest123   → hash below
-- ============================================================
INSERT INTO users (username, email, password_hash, role) VALUES
    ('Admin',        'admin@infinity-void.kz',   '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin'),
    ('Арман',        'arman@infinity-void.kz',   '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'guest'),
    ('Болат',        'bolat@infinity-void.kz',   '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'guest'),
    ('Аида',         'aida@infinity-void.kz',    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'guest'),
    ('Мадина',       'madina@infinity-void.kz',  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'staff'),
    ('Дамир',        'damir@infinity-void.kz',   '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'guest'),
    ('Жансая',       'zhansaya@infinity-void.kz','$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'guest'),
    ('Нурлан',       'nurlan@infinity-void.kz',  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'guest');

-- ============================================================
--  SEED DATA — rooms (floors 1-5, types Standard & Lux)
-- ============================================================
INSERT INTO rooms (room_number, type, floor, capacity, price, description) VALUES
    (101, 'Standard', 1, 2, 5000.00,  'Comfortable twin room on ground floor'),
    (102, 'Standard', 1, 2, 5000.00,  'Double room with garden view'),
    (103, 'Standard', 1, 1, 4500.00,  'Single room, quiet and cozy'),
    (104, 'Lux',      1, 2, 15000.00, 'Lux suite with living area'),
    (201, 'Standard', 2, 2, 5500.00,  'Twin room with mountain view'),
    (202, 'Standard', 2, 2, 5500.00,  'Double room, renovated 2024'),
    (203, 'Standard', 2, 3, 7000.00,  'Triple room for families'),
    (204, 'Lux',      2, 2, 16000.00, 'Premium lux with jacuzzi'),
    (301, 'Standard', 3, 2, 5500.00,  'Standard room with city view'),
    (302, 'Standard', 3, 2, 5500.00,  'Deluxe standard room'),
    (303, 'Lux',      3, 4, 20000.00, 'Family lux suite, 2 bedrooms'),
    (304, 'Lux',      3, 2, 17000.00, 'Executive lux with workspace'),
    (401, 'Standard', 4, 2, 6000.00,  'Superior standard room'),
    (402, 'Standard', 4, 2, 6000.00,  'Standard with panoramic window'),
    (403, 'Lux',      4, 2, 18000.00, 'Junior suite with balcony'),
    (404, 'Lux',      4, 4, 25000.00, 'Presidential suite'),
    (501, 'Standard', 5, 2, 6500.00,  'Top floor standard room'),
    (502, 'Lux',      5, 2, 20000.00, 'Penthouse lux room'),
    (503, 'Lux',      5, 6, 35000.00, 'Grand penthouse suite');

-- ============================================================
--  SEED DATA — bookings
-- ============================================================
INSERT INTO bookings (user_id, room_id, check_in, check_out, total_price, status) VALUES
    (2, 1,  '2025-06-01', '2025-06-05', 20000.00,  'completed'),
    (3, 5,  '2025-06-10', '2025-06-12', 11000.00,  'completed'),
    (4, 4,  '2025-07-01', '2025-07-03', 30000.00,  'completed'),
    (6, 2,  '2025-07-15', '2025-07-20', 25000.00,  'completed'),
    (7, 8,  '2025-08-01', '2025-08-07', 96000.00,  'completed'),
    (2, 12, '2025-09-01', '2025-09-03', 34000.00,  'confirmed'),
    (3, 16, '2025-09-10', '2025-09-15', 125000.00, 'confirmed'),
    (8, 6,  '2025-10-01', '2025-10-04', 16500.00,  'confirmed');

-- ============================================================
--  USEFUL QUERIES — for testing and presentation
-- ============================================================

-- 1. All available rooms with price
-- SELECT id, room_number, type, floor, price
-- FROM rooms WHERE is_available = TRUE ORDER BY price;

-- 2. User with their bookings (JOIN)
-- SELECT u.username, u.email, b.check_in, b.check_out, b.total_price, r.room_number
-- FROM bookings b
-- JOIN users u ON b.user_id = u.id
-- JOIN rooms r ON b.room_id = r.id
-- ORDER BY b.check_in;

-- 3. Revenue by room type
-- SELECT r.type, COUNT(b.id) AS bookings, SUM(b.total_price) AS revenue
-- FROM bookings b JOIN rooms r ON b.room_id = r.id
-- GROUP BY r.type;

-- 4. Most booked rooms
-- SELECT r.room_number, r.type, COUNT(b.id) AS times_booked
-- FROM rooms r LEFT JOIN bookings b ON r.id = b.room_id
-- GROUP BY r.id, r.room_number, r.type
-- ORDER BY times_booked DESC;

-- 5. Available Lux rooms under 20000
-- SELECT room_number, floor, price, description
-- FROM rooms
-- WHERE type = 'Lux' AND is_available = TRUE AND price < 20000
-- ORDER BY price;
