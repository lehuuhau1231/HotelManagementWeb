import hashlib

from app.models import User, Room, RoomType, Customer, CustomerType, Guest, RoomReservationForm, RoomRentalForm, \
    BookingStatus, Comment
from app import db, app
import cloudinary.uploader
from sqlalchemy import or_, desc, exists
import hmac
from urllib.parse import urlencode
import urllib.parse
from datetime import datetime, timedelta


def check_room_availability(room_id, checkin, checkout):
    room_reservation = RoomReservationForm.query.filter(RoomReservationForm.room_id == room_id).all()
    room_rental = RoomRentalForm.query.filter(RoomRentalForm.room_id == room_id).all()
    is_available = True

    for room in room_reservation:
        if not ((checkin > room.check_out_date) or (checkout < room.check_in_date)):#checkin, checkout khong nam trong khoang phieu dat
            is_available = False
            break

    if is_available:
        for room in room_rental:
            if not ((checkin > room.check_out_date) or (checkout < room.check_in_date)):
                is_available = False
                break

    return is_available


def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))
    if role:
        u = u.filter(User.role.__eq__(role))

    return u.first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_by_account(table, account):
    account = account.strip()
    return table.query.filter(
        or_(table.username == account, table.email == account)).first()


def get_customer_by_account(table, account):
    account = account.strip()
    return table.query.filter(
        or_(table.username == account, table.email == account, table.identification_card == account)).first()


def add_customer(name, username, password, email, phone, avatar, gender, identification, type):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    if type.__eq__('Domestic'):
        type = 1
    else:
        type = 2
    user = Customer(name=name, username=username, password=password, email=email, phone=phone, gender=gender
                    , identification_card=identification, customer_type_id=type)
    if avatar:
        upload_result = cloudinary.uploader.upload(avatar)
        user.avatar = upload_result.get('secure_url')
    db.session.add(user)
    db.session.commit()


def existence_check(table, attribute, value):
    return table.query.filter(getattr(table, attribute).__eq__(value)).first()


def change_password(user_id, new_password):
    new_password = str(hashlib.md5(new_password.strip().encode('utf-8')).hexdigest())
    user = get_user_by_id(user_id)
    if user:
        user.password = new_password
        db.session.commit()


def load_room(checkin=None, checkout=None, page=None, room_type=None, room_id=None):
    rooms = Room.query

    if room_type:
        rooms = rooms.join(RoomType).filter(RoomType.name == room_type)

    new_room = []
    if checkin and checkout:
        if checkin <= checkout:
            for room in rooms:
                if check_room_availability(checkin, checkout, room.id):
                    new_room.append(room)

            # Thêm logic phân trang cho new_room
            if page:
                page_size = app.config["PAGE_SIZE"]
                start = (page - 1) * page_size
                end = start + page_size
                return new_room[start:end], len(new_room)
            return new_room, len(new_room)

    if room_id:
        return rooms.filter(Room.id == room_id).first()

    length = rooms.count()
    if page:
        page_size = app.config["PAGE_SIZE"]
        start = (page - 1) * page_size
        rooms = rooms.slice(start, start + page_size)

    return rooms.all(), length


def count_room():
    return Room.query.count()


def get_customer_type(type=None):
    if type:
        return CustomerType.query.filter(CustomerType.type == type).first()
    return CustomerType.query.all()


def add_guest(data):
    if data['customer_type'].__eq__('Domestic'):
        type = 1
    else:
        type = 2
    guest = Guest(name=data['name'], identification_card=data['identification_card'], customer_type_id=type)
    db.session.add(guest)


def add_room_reservation_form(data, customer_id, user_id=None):
    if user_id:
        room_reservation_form = RoomReservationForm(check_in_date=data['check_in_date'],
                                                    check_out_date=data['check_out_date'],
                                                    deposit=data['deposit'], total_amount=data['total_amount'],
                                                    room_id=data['room_id'], customer_id=customer_id, user_id=user_id)
    else:
        room_reservation_form = RoomReservationForm(check_in_date=data['check_in_date'],
                                                    check_out_date=data['check_out_date'],
                                                    deposit=data['deposit'], total_amount=data['total_amount'],
                                                    room_id=data['room_id'], customer_id=customer_id)
    db.session.add(room_reservation_form)


def get_form(table, form_id=None):
    if form_id:
        return table.query.get(form_id)
    return table.query.order_by(desc(table.id)).first()


def get_form_by_id(table, id):
    return table.query.filter(table.id == id).first()


def get_reservation_form_not_exist_rental(customer_id=None):
    if customer_id:
        return (db.session.query(RoomReservationForm)
                .join(Customer, RoomReservationForm.customer_id == Customer.cus_id)
                .filter(Customer.identification_card == customer_id)
                .order_by(desc(RoomReservationForm.check_in_date)).all())

    return (db.session.query(RoomReservationForm)  # lay ds phieu dat chua duoc tao thanh phieu thue
            .filter(RoomReservationForm.status.__eq__(BookingStatus.CONFIRMED)).order_by(
        desc(RoomReservationForm.check_in_date)).all())


def get_room_rental_form_all(customer_id=None):
    if customer_id:
        return (db.session.query(RoomRentalForm)
                .join(Customer, RoomRentalForm.customer_id == Customer.cus_id)
                .filter(Customer.identification_card == customer_id)
                .order_by(desc(RoomRentalForm.check_out_date)).all())

    return (RoomRentalForm.query.filter(RoomRentalForm.status.__eq__(BookingStatus.IN_USE))
            .order_by(desc(RoomRentalForm.check_out_date)).all())


def get_rented_room(customer_id):
    return RoomRentalForm.query.filter(RoomRentalForm.status.__eq__(BookingStatus.COMPLETED),
                                       RoomRentalForm.customer_id == customer_id).all()


def load_comment(room_id):
    return Comment.query.filter(Comment.room_id == room_id).order_by(-Comment.id).all()


def get_comments(room_id, page=1):
    page_size = app.config["COMMENT_SIZE"]
    total_comments = Comment.query.filter(Comment.room_id == room_id).count()
    start = (page - 1) * page_size
    comments = Comment.query.filter(Comment.room_id == room_id) \
        .order_by(Comment.id.desc()) \
        .offset(start) \
        .limit(page_size) \
        .all()

    return {
        "comments": comments,
        "total": total_comments,
        "page": page,
        "page_size": page_size
    }


def cancel_form():
    days_ago = datetime.now() - timedelta(days=28)
    with app.app_context():
        room_reservation_form = RoomReservationForm.query.filter(RoomReservationForm.check_in_date < days_ago,
                                                                 RoomReservationForm.status == BookingStatus.CONFIRMED).all()
        print('chay')
        for item in room_reservation_form:
            item.status = BookingStatus.CANCELLED

        db.session.commit()


class vnpay:
    requestData = {}
    responseData = {}

    def get_payment_url(self, vnpay_payment_url, secret_key):
        # Dữ liệu thanh toán được sắp xếp dưới dạng danh sách các cặp khóa-giá trị theo thứ tự tăng dần của khóa.
        inputData = sorted(self.requestData.items())
        # Duyệt qua danh sách đã sắp xếp và tạo chuỗi query sử dụng urllib.parse.quote_plus để mã hóa giá trị
        queryString = ''
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        # Sử dụng phương thức __hmacsha512 để tạo mã hash từ chuỗi query và khóa bí mật
        hashValue = self.__hmacsha512(secret_key, queryString)
        return vnpay_payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def validate_response(self, secret_key):
        # Lấy giá trị của vnp_SecureHash từ self.responseData.
        vnp_SecureHash = self.responseData['vnp_SecureHash']
        # Loại bỏ các tham số liên quan đến mã hash
        if 'vnp_SecureHash' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHashType')
        # Sắp xếp dữ liệu (inputData)
        inputData = sorted(self.responseData.items())

        hasData = ''
        seq = 0
        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    hasData = hasData + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    hasData = str(key) + '=' + urllib.parse.quote_plus(str(val))
        # Tạo mã hash
        hashValue = self.__hmacsha512(secret_key, hasData)

        print(
            'Validate debug, HashData:' + hasData + "\n HashValue:" + hashValue + "\nInputHash:" + vnp_SecureHash)

        return vnp_SecureHash == hashValue

    # tạo mã hash dựa trên thuật toán HMAC-SHA-512
    @staticmethod
    def __hmacsha512(key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()
