from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, validator
import bcrypt
from typing import Optional
from datetime import date

DATABASE_URL = "sqlite:///./hotel.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(Integer, unique=True, nullable=False)
    type = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    total_price = Column(Float)
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")


Base.metadata.create_all(bind=engine)


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @validator("username")
    def username_not_empty(cls, v):
        if not v or len(v) < 2:
            raise ValueError("Имя пользователя должно быть не менее 2 символов")
        return v

    @validator("email")
    def email_must_have_at(cls, v):
        if "@" not in v:
            raise ValueError("Некорректный email")
        return v

    @validator("password")
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError("Пароль должен быть не менее 6 символов")
        return v


class RoomCreate(BaseModel):
    room_number: int
    type: str
    price: float
    is_available: bool = True

    @validator("type")
    def type_valid(cls, v):
        if v not in ["Standard", "Lux"]:
            raise ValueError("Тип комнаты: только Standard или Lux")
        return v

    @validator("price")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("Цена должна быть больше 0")
        return v


class BookingCreate(BaseModel):
    user_id: int
    room_id: int
    check_in: date
    check_out: date

    @validator("check_out")
    def check_out_after_check_in(cls, v, values):
        if "check_in" in values and v <= values["check_in"]:
            raise ValueError("Дата выезда должна быть позже даты заезда")
        return v


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="Infinity-Void Hotel API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Қонақүй жүйесі жұмыс істеп тұр!", "status": "ok"}


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]


@app.post("/users", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = User(username=user.username, email=user.email, password_hash=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Пользователь создан", "id": new_user.id, "username": new_user.username}


@app.put("/users/{user_id}")
def update_user(user_id: int, username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.username = username
    db.commit()
    return {"message": "Обновлено", "username": user.username}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    for booking in bookings:
        room = db.query(Room).filter(Room.id == booking.room_id).first()
        if room:
            room.is_available = True
        db.delete(booking)
    db.delete(user)
    db.commit()
    return {"message": f"Пользователь {user.username} удалён"}


@app.get("/rooms")
def get_rooms(type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Room)
    if type:
        query = query.filter(Room.type == type)
    return query.all()


@app.get("/rooms/{room_id}")
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    return room


@app.post("/rooms", status_code=201)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    existing = db.query(Room).filter(Room.room_number == room.room_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Номер комнаты уже существует")
    new_room = Room(**room.dict())
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room


@app.put("/rooms/{room_id}")
def update_room(room_id: int, room: RoomCreate, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    for key, value in room.dict().items():
        setattr(db_room, key, value)
    db.commit()
    return db_room


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    bookings = db.query(Booking).filter(Booking.room_id == room_id).all()
    for booking in bookings:
        db.delete(booking)
    db.delete(room)
    db.commit()
    return {"message": f"Комната {room_id} удалена"}


@app.get("/bookings")
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "user": {"id": b.user.id, "username": b.user.username},
            "room": {"id": b.room.id, "room_number": b.room.room_number, "type": b.room.type},
            "check_in": b.check_in,
            "check_out": b.check_out,
            "total_price": b.total_price
        })
    return result


@app.post("/bookings", status_code=201)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == booking.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    if not room.is_available:
        raise HTTPException(status_code=400, detail="Комната недоступна")
    days = (booking.check_out - booking.check_in).days
    total = room.price * days
    new_booking = Booking(
        user_id=booking.user_id,
        room_id=booking.room_id,
        check_in=booking.check_in,
        check_out=booking.check_out,
        total_price=total
    )
    room.is_available = False
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return {"message": "Бронь создана", "id": new_booking.id, "total_price": total}


@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронь не найдена")
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if room:
        room.is_available = True
    db.delete(booking)
    db.commit()
    return {"message": f"Бронь {booking_id} отменена"}


@app.post("/login")
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email).first()
    if not user or not bcrypt.checkpw(creds.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    return {"message": "Вход выполнен", "user_id": user.id, "username": user.username}


app.mount("/static", StaticFiles(directory="static"), name="static")