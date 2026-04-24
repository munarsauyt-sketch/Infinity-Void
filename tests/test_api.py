import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app, Base, get_db

TEST_DB_URL = "sqlite:///./test_hotel.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user(client):
    r = client.post("/register", json={"username": "Арман", "email": "arman@test.kz", "password": "password123"})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def room(client):
    r = client.post("/rooms", json={"room_number": 101, "type": "Standard", "price": 5000})
    assert r.status_code == 201
    return r.json()


# ----- Auth -----

def test_register(client):
    r = client.post("/register", json={"username": "Болат", "email": "bolat@test.kz", "password": "securepass"})
    assert r.status_code == 201
    assert "id" in r.json()


def test_register_duplicate_email(client):
    data = {"username": "Ак", "email": "dup@test.kz", "password": "password1"}
    client.post("/register", json=data)
    r = client.post("/register", json=data)
    assert r.status_code == 400


def test_login_success(client, user):
    r = client.post("/login", json={"email": "arman@test.kz", "password": "password123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client, user):
    r = client.post("/login", json={"email": "arman@test.kz", "password": "wrongpass"})
    assert r.status_code == 401


def test_login_unknown_email(client):
    r = client.post("/login", json={"email": "nobody@test.kz", "password": "pass"})
    assert r.status_code == 401


# ----- Validation -----

def test_register_short_password(client):
    r = client.post("/register", json={"username": "X", "email": "x@x.com", "password": "short"})
    assert r.status_code == 422


def test_register_invalid_email(client):
    r = client.post("/register", json={"username": "X", "email": "notanemail", "password": "longpassword"})
    assert r.status_code == 422


def test_room_invalid_type(client):
    r = client.post("/rooms", json={"room_number": 1, "type": "Suite", "price": 1000})
    assert r.status_code == 422


def test_room_zero_price(client):
    r = client.post("/rooms", json={"room_number": 2, "type": "Lux", "price": 0})
    assert r.status_code == 422


# ----- Rooms CRUD -----

def test_create_room(client):
    r = client.post("/rooms", json={"room_number": 201, "type": "Lux", "price": 15000})
    assert r.status_code == 201
    assert r.json()["room_number"] == 201


def test_get_rooms(client, room):
    r = client.get("/rooms")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_filter_rooms_by_type(client):
    client.post("/rooms", json={"room_number": 301, "type": "Standard", "price": 5000})
    client.post("/rooms", json={"room_number": 302, "type": "Lux", "price": 12000})
    r = client.get("/rooms?type=Lux")
    assert all(room["type"] == "Lux" for room in r.json())


def test_filter_rooms_by_availability(client, room):
    r = client.get("/rooms?available=true")
    assert all(room["is_available"] for room in r.json())


def test_update_room(client, room):
    r = client.put(f"/rooms/{room['id']}", json={"room_number": 101, "type": "Lux", "price": 20000})
    assert r.status_code == 200
    assert r.json()["type"] == "Lux"


def test_delete_room(client, room):
    r = client.delete(f"/rooms/{room['id']}")
    assert r.status_code == 200
    r2 = client.get(f"/rooms/{room['id']}")
    assert r2.status_code == 404


# ----- Bookings CRUD -----

def test_create_booking(client, user, room):
    r = client.post("/bookings", json={
        "user_id": user["id"], "room_id": room["id"],
        "check_in": "2025-06-01", "check_out": "2025-06-05"
    })
    assert r.status_code == 201
    assert r.json()["total_price"] == 5000 * 4


def test_booking_sets_room_unavailable(client, user, room):
    client.post("/bookings", json={
        "user_id": user["id"], "room_id": room["id"],
        "check_in": "2025-07-01", "check_out": "2025-07-03"
    })
    r = client.get(f"/rooms/{room['id']}")
    assert r.json()["is_available"] is False


def test_booking_unavailable_room(client, user, room):
    client.post("/bookings", json={
        "user_id": user["id"], "room_id": room["id"],
        "check_in": "2025-08-01", "check_out": "2025-08-03"
    })
    r = client.post("/bookings", json={
        "user_id": user["id"], "room_id": room["id"],
        "check_in": "2025-08-10", "check_out": "2025-08-12"
    })
    assert r.status_code == 400


def test_cancel_booking_restores_room(client, user, room):
    b = client.post("/bookings", json={
        "user_id": user["id"], "room_id": room["id"],
        "check_in": "2025-09-01", "check_out": "2025-09-04"
    }).json()
    client.delete(f"/bookings/{b['id']}")
    r = client.get(f"/rooms/{room['id']}")
    assert r.json()["is_available"] is True


def test_filter_bookings_by_user(client, user, room):
    client.post("/bookings", json={
        "user_id": user["id"], "room_id": room["id"],
        "check_in": "2025-10-01", "check_out": "2025-10-02"
    })
    r = client.get(f"/bookings?user_id={user['id']}")
    assert all(b["user"]["id"] == user["id"] for b in r.json())


# ----- JOIN query -----

def test_user_bookings_join(client, user, room):
    client.post("/bookings", json={
        "user_id": user["id"], "room_id": room["id"],
        "check_in": "2025-11-01", "check_out": "2025-11-03"
    })
    r = client.get(f"/users/{user['id']}/bookings")
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["id"] == user["id"]
    assert len(data["bookings"]) == 1
    assert "room" in data["bookings"][0]
