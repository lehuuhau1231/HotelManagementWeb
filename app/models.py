from datetime import datetime

from cloudinary.utils import unique
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Relationship
from enum import Enum as RoleEnum
from app import db, app


class Role(RoleEnum):
    ADMIN = 1,
    RECEPTIONIST = 2,
    CUSTOMER = 3


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)


class CustomerType(Base):
    type = Column(String(10), default="Trong nước")
    user = Relationship('User', backref='customer_type', lazy='True')
    customer_regulation = Relationship('CustomerRegulation', backref='customer_type', lazy='True')


class User(Base):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phone = Column(String(10), nullable=False)
    avatar = Column(String(100),
                    default="https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg")
    gender = Column(Boolean, default=True)  # True is Man
    IDCard = Column(String(12), nullable=False, unique=True)
    role = Column(Enum(Role), default=Role.CUSTOMER)
    address = Column(String(100))
    room = Relationship('Room', backref='user', lazy='True')
    room_regulation = Relationship('RoomRegulation', backref='user', lazy='True')
    extra_charge_regulation = Relationship('ExtraChargeRegulation', backref='user', lazy='True')
    customer_regulation = Relationship('CustomerRegulation', backref='user', lazy='True')
    room_reservation_form = Relationship('RoomReservationForm', backref='user', lazy='True')
    bill = Relationship('Bill', backref='user', lazy='True')
    room_rental_from = Relationship('RoomRentalFrom', backref='user', lazy='True')
    comment = Relationship('Comment', backref='user', lazy='True', cascade='all, delete-orphan')
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False)


class RoomType(Base):
    name = Column(String(50), nullable=False, unique=True)
    room = Relationship('Room', backref='room_type', lazy='True')
    room_regulation = Relationship('RoomRegulation', back_populates='room_type', uselist=False, cascade='all, delete-orphan')


class Room(Base):
    name = Column(String(50), nullable=False)
    image = Column(String(100))
    price = Column(Float, nullable=False)
    room_reservation_from = Relationship('RoomReservationFrom', backref='room', lazy='True')
    room_rental_from = Relationship('RoomRentalFrom', backref='room', lazy='True')
    comment = Relationship('Comment', backref='room', lazy='True')
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)


class RoomRegulation(Base):
    number_of_guests = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), unique=True, nullable=False)
    room_type = Relationship('RoomType', back_populates='room_regulation')
    extra_charge_regulation = Relationship('ExtraChargeRegulation', backref='room', lazy='True')


class ExtraChargeRegulation(Base):
    rate = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_regulation_id = Column(Integer, ForeignKey(RoomRegulation.id), nullable=False, unique=True)


class CustomerRegulation(Base):
    Coefficient = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False, unique=True)


class RoomReservationForm(Base):
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    is_check_in = Column(Boolean, nullable=False)
    deposit = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)


class Bill(Base):
    total_amount = Column(Float, nullable=False)
    creation_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_rental_from = Relationship('RoomRentalFrom', backref='bill', lazy='True')


class RoomRentalForm(Base):
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    deposit = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    bill_id = Column(Integer, ForeignKey(Bill.id), nullable=False, unique=True)


class Comment(Base):
    content = Column(String(1000), nullable=False)
    creation_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        # db.create_all()
