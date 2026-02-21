from fastapi import FastAPI, HTTPException
from typing import List
from schemas import UserCreate, RoomCreate, BookingCreate

app = FastAPI()

db = {
    "users": [],
    "rooms": [
        {"id": 1, "room_number": 101, "type": "Lux", "price": 25000, "is_available": True}
    ],
    "bookings": []
}

@app.get("/")
def home():
    return {"message": "Қонақүй жүйесі жұмыс істеп тұр!"}

@app.get("/rooms")
def get_rooms():
    return db["rooms"]

@app.post("/bookings")
def create_booking(booking: BookingCreate):
    db["bookings"].append(booking.dict())
    return {"message": "Бронь сәтті жасалды!", "data": booking}

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int):
    return {"message": f"ID {booking_id} бойынша бронь жойылды"}
