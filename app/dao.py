import hashlib
from app.models import User, Room, RoomType
from app import db, app
import cloudinary.uploader


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_by_account(account):
    return User.query.filter(User.username.__eq__(account) or User.email.__eq__(account)).first()


def add_user(name, username, password, email, phone, avatar, gender, identification, type):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    if type.__eq__('domestic'):
        type = 1
    else:
        type = 2
    user = User(name=name, username=username, password=password, email=email, phone=phone, gender=gender
                , identification_card=identification, customer_type_id=type)
    if avatar:
        upload_result = cloudinary.uploader.upload(avatar)
        user.avatar = upload_result.get('secure_url')
    db.session.add(user)
    db.session.commit()


def existence_check(attribute, value):
    return User.query.filter(getattr(User, attribute).__eq__(value)).first()


def change_password(user_id, new_password):
    new_password = str(hashlib.md5(new_password.strip().encode('utf-8')).hexdigest())
    user = get_user_by_id(user_id)
    if user:
        user.password = new_password
        db.session.commit()

        
def load_room(page=None, room_type=None, room_id=None):
    rooms = Room.query

    if room_type:
        rooms = rooms.join(RoomType).filter(RoomType.name == room_type)

    if room_id:
        return rooms.filter(Room.id == room_id).first()

    if page:
        page_size = app.config["PAGE_SIZE"]
        start = (page - 1) * page_size
        rooms = rooms.slice(start, start + page_size)

    return rooms.all()


def count_room():
    return Room.query.count()
