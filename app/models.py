from configparser import Interpolation
from datetime import datetime
import hashlib
from cloudinary.utils import unique
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, text
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum
from app import db, app
from flask_login import UserMixin


class Role(RoleEnum):
    ADMIN = 1,
    RECEPTIONIST = 2,
    CUSTOMER = 3


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)


class CustomerType(Base):
    type = Column(String(10))
    user = relationship('User', backref='customer_type', lazy=True)
    customer_regulation = relationship('CustomerRegulation', backref='customer_type', lazy=True)


class User(Base, UserMixin):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phone = Column(String(10), nullable=False)
    avatar = Column(String(100),
                    default="https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg")
    gender = Column(String(6), nullable=False)
    identification_card = Column(String(12), nullable=False, unique=True)
    role = Column(Enum(Role), default=Role.CUSTOMER)
    room = relationship('Room', backref='user', lazy=True)
    room_regulation = relationship('RoomRegulation', backref='user', lazy=True)
    extra_charge_regulation = relationship('ExtraChargeRegulation', backref='user', lazy=True)
    customer_regulation = relationship('CustomerRegulation', backref='user', lazy=True)
    room_reservation_form = relationship('RoomReservationForm', backref='user', lazy=True)
    bill = relationship('Bill', backref='user', lazy=True)
    room_rental_from = relationship('RoomRentalForm', backref='user', lazy=True)
    comment = relationship('Comment', backref='user', cascade='all, delete-orphan', lazy=True)
    customer_type_id = Column(Integer, ForeignKey(CustomerType.id), nullable=False, default=1)


class RoomType(Base):
    name = Column(String(50), nullable=False, unique=True)
    room = relationship('Room', backref='room_type', lazy=True)
    room_regulation = relationship('RoomRegulation', backref='room_type', uselist=False)


class Room(Base):
    name = Column(String(50), nullable=False)
    image = Column(String(100))
    price = Column(Float, nullable=False)
    room_reservation_from = relationship('RoomReservationForm', backref='room', lazy=True)
    room_rental_from = relationship('RoomRentalForm', backref='room', lazy=True)
    comment = relationship('Comment', backref='room', lazy=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)


class RoomRegulation(Base):
    number_of_guests = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_type_id = Column(Integer, ForeignKey(RoomType.id), unique=True, nullable=False)
    extra_charge_regulation = relationship('ExtraChargeRegulation', backref='room', cascade='all, delete-orphan',
                                           lazy=True)


class ExtraChargeRegulation(Base):
    rate = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_regulation_id = Column(Integer, ForeignKey(RoomRegulation.id, ondelete='CASCADE'), nullable=False, unique=True)


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
    room_rental_from = relationship('RoomRentalForm', backref='bill', cascade='all, delete-orphan', lazy=True)


class RoomRentalForm(Base):
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    deposit = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    bill_id = Column(Integer, ForeignKey(Bill.id, ondelete='CASCADE'), nullable=False, unique=True)


class Comment(Base):
    content = Column(String(1000), nullable=False)
    creation_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        customer_type1 = CustomerType(type='domestic')
        customer_type2 = CustomerType(type='foreign')
        # db.session.query(User).delete()
        # db.session.execute(text('ALTER TABLE user AUTO_INCREMENT = 1')) #Reset AUTO_INCREMENT về 1 khi xóa bảng và thêm mới
        db.session.add_all([customer_type1, customer_type2])
        db.session.commit()
        customer_type = db.session.query(CustomerType).filter(CustomerType.type.__eq__('domestic')).first()
        user1 = User(name='Lê Hữu Hậu', username='lehuuhau',
                     password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()), email='lehuuhau1231@gmail.com',
                     phone='0378151028',
                     gender=1, identification_card='06424016252', customer_type_id=customer_type.id)
        db.session.add(user1)
        db.session.commit()

        #         ==============================Thêm loại phòng======================================

        room_type_single = RoomType(type='Single Bedroom')
        room_type_twin = RoomType(type='Twin Bedroom')
        room_type_double = RoomType(type='Double Bedroom')

        db.session.add_all([room_type_single, room_type_twin, room_type_double])
        db.session.commit()

        #         ==============================Thêm phòng======================================

        room1 = Room()
# name = Column(String(50), nullable=False)
#     username = Column(String(50), nullable=False, unique=True)
#     password = Column(String(50), nullable=False)
#     email = Column(String(50), nullable=False, unique=True)
#     phone = Column(String(10), nullable=False)
#     avatar = Column(String(100),
#                     default="https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg")
#     gender = Column(Boolean, default=True)  # True is Man
#     IDCard = Column(String(12), nullable=False, unique=True)
#     role = Column(Enum(Role), default=Role.CUSTOMER)
#     address = Column(String(100))
