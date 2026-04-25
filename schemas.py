"""
========================================================
 Infinity-Void Hotel Management System
 Pydantic Schemas v2.0
 Author: 3rd team member
 Description: Full request/response schemas with
              validation, examples and documentation
========================================================
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import date, datetime
from typing import Optional, List
import re


# ============================================================
#  AUTH SCHEMAS
# ============================================================

class RegisterRequest(BaseModel):
    """Schema for user registration."""
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Display name of the user",
        examples=["Арман Сейткали"]
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address, must be unique",
        examples=["arman@example.kz"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 chars)",
        examples=["securePass123"]
    )

    @field_validator("username")
    @classmethod
    def username_no_special_chars(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[\w\s\-\.]+$", v, re.UNICODE):
            raise ValueError("Username contains invalid characters")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if v.isdigit():
            raise ValueError("Password cannot be all digits")
        if v.isalpha():
            raise ValueError("Password must contain at least one digit")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "Арман",
                "email": "arman@infinity-void.kz",
                "password": "securePass1"
            }
        }
    }


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., examples=["arman@infinity-void.kz"])
    password: str   = Field(..., min_length=1, examples=["securePass1"])

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "arman@infinity-void.kz",
                "password": "securePass1"
            }
        }
    }


class TokenResponse(BaseModel):
    """Returned after successful login."""
    access_token: str
    token_type:   str = "bearer"
    user_id:      int
    username:     str


# ============================================================
#  USER SCHEMAS
# ============================================================

class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email:    EmailStr


class UserCreate(UserBase):
    """Full user creation schema (also used for /register endpoint)."""
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        return v.strip()


class UserUpdate(BaseModel):
    """Schema for updating user profile fields."""
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email:    Optional[EmailStr] = None


class UserResponse(BaseModel):
    """Public user data returned by the API."""
    id:         int
    username:   str
    email:      str
    is_active:  bool = True
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Paginated list of users."""
    total:  int
    users:  List[UserResponse]


# ============================================================
#  ROOM SCHEMAS
# ============================================================

class RoomBase(BaseModel):
    room_number:  int   = Field(..., gt=0, le=9999,   description="Unique room number")
    type:         str   = Field(...,                   description="Room type: Standard or Lux")
    price:        float = Field(..., gt=0, le=1000000, description="Price per night in KZT")
    is_available: bool  = Field(True,                  description="Whether room is available for booking")


class RoomCreate(RoomBase):
    """Schema for creating a new room."""
    floor:       Optional[int]  = Field(1,    ge=1, le=50)
    capacity:    Optional[int]  = Field(2,    ge=1, le=10)
    description: Optional[str]  = Field(None, max_length=500)

    @field_validator("type")
    @classmethod
    def validate_room_type(cls, v: str) -> str:
        allowed = {"Standard", "Lux"}
        if v not in allowed:
            raise ValueError(f"Room type must be one of: {', '.join(allowed)}")
        return v

    @field_validator("price")
    @classmethod
    def round_price(cls, v: float) -> float:
        return round(v, 2)

    model_config = {
        "json_schema_extra": {
            "example": {
                "room_number": 201,
                "type": "Standard",
                "price": 5500.00,
                "floor": 2,
                "capacity": 2,
                "description": "Double room with city view",
                "is_available": True
            }
        }
    }


class RoomUpdate(BaseModel):
    """Schema for partial room update (all fields optional)."""
    room_number:  Optional[int]   = Field(None, gt=0, le=9999)
    type:         Optional[str]   = None
    price:        Optional[float] = Field(None, gt=0)
    is_available: Optional[bool]  = None
    floor:        Optional[int]   = Field(None, ge=1, le=50)
    capacity:     Optional[int]   = Field(None, ge=1, le=10)
    description:  Optional[str]   = Field(None, max_length=500)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in {"Standard", "Lux"}:
            raise ValueError("Room type must be Standard or Lux")
        return v


class RoomResponse(RoomBase):
    """Full room data returned by API."""
    id:          int
    floor:       Optional[int] = 1
    capacity:    Optional[int] = 2
    description: Optional[str] = None
    created_at:  Optional[datetime] = None

    model_config = {"from_attributes": True}


class RoomListResponse(BaseModel):
    total: int
    rooms: List[RoomResponse]


# ============================================================
#  BOOKING SCHEMAS
# ============================================================

class BookingCreate(BaseModel):
    """Schema for creating a new booking."""
    user_id:   int  = Field(..., gt=0, description="ID of the user making the booking")
    room_id:   int  = Field(..., gt=0, description="ID of the room to book")
    check_in:  date = Field(..., description="Arrival date (YYYY-MM-DD)")
    check_out: date = Field(..., description="Departure date (YYYY-MM-DD)")
    notes:     Optional[str] = Field(None, max_length=500, description="Special requests")

    @field_validator("check_in")
    @classmethod
    def check_in_not_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Check-in date cannot be in the past")
        return v

    @model_validator(mode="after")
    def dates_valid(self) -> "BookingCreate":
        if self.check_in and self.check_out:
            if self.check_out <= self.check_in:
                raise ValueError("Check-out must be after check-in")
            nights = (self.check_out - self.check_in).days
            if nights > 365:
                raise ValueError("Booking cannot exceed 365 nights")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "room_id": 3,
                "check_in": "2025-07-01",
                "check_out": "2025-07-05",
                "notes": "Late check-in requested"
            }
        }
    }


class BookingUpdate(BaseModel):
    """Schema for updating booking dates or notes."""
    check_in:  Optional[date] = None
    check_out: Optional[date] = None
    notes:     Optional[str]  = Field(None, max_length=500)
    status:    Optional[str]  = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in {"confirmed", "cancelled", "completed"}:
            raise ValueError("Status must be: confirmed, cancelled or completed")
        return v


class BookingRoomInfo(BaseModel):
    """Nested room info inside booking response."""
    id:          int
    room_number: int
    type:        str
    price:       float

    model_config = {"from_attributes": True}


class BookingUserInfo(BaseModel):
    """Nested user info inside booking response."""
    id:       int
    username: str

    model_config = {"from_attributes": True}


class BookingResponse(BaseModel):
    """Full booking data returned by API."""
    id:          int
    user:        BookingUserInfo
    room:        BookingRoomInfo
    check_in:    date
    check_out:   date
    total_price: Optional[float] = None
    status:      Optional[str]   = "confirmed"
    notes:       Optional[str]   = None
    created_at:  Optional[datetime] = None

    model_config = {"from_attributes": True}


class BookingListResponse(BaseModel):
    total:    int
    bookings: List[BookingResponse]


# ============================================================
#  COMBINED / NESTED SCHEMAS
# ============================================================

class UserWithBookings(BaseModel):
    """User profile with all their bookings (JOIN response)."""
    user:     UserResponse
    bookings: List[BookingResponse]
    total:    int = 0

    model_config = {"from_attributes": True}


class RoomWithBookings(BaseModel):
    """Room details with its booking history."""
    room:     RoomResponse
    bookings: List[BookingResponse]
    total:    int = 0


# ============================================================
#  GENERIC RESPONSE SCHEMAS
# ============================================================

class MessageResponse(BaseModel):
    """Simple success message."""
    message: str
    id:      Optional[int]   = None
    detail:  Optional[str]   = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    code:   Optional[int]  = None
    field:  Optional[str]  = None


class HealthResponse(BaseModel):
    """API health check response."""
    message:  str
    status:   str
    version:  str  = "1.0"
    database: str  = "connected"
