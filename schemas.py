from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # Электрондық поштаның дұрыстығын тексереді
    password: str = Field(..., min_length=8) # Құпия сөз кемі 8 символ

class RoomCreate(BaseModel):
    room_number: int
    type: str
    price: float = Field(..., gt=0) # Бағасы 0-ден көп болуы керек
    is_available: bool = True

class BookingCreate(BaseModel):
    user_id: int
    room_id: int
    check_in: date
    check_out: date