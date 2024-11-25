import hashlib
from app.models import User
from app import db
import cloudinary.uploader


def auth_user(username,password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username) and User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_user(name, username, password, email, phone, avatar, gender, identification, type):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    if type.__eq__('domestic'):
        type = 1
    else:
        type = 2
    user = User(name=name, username=username, password=password, email=email, phone=phone, gender=gender
                ,identification_card=identification, customer_type_id=type)
    if avatar:
        upload_result = cloudinary.uploader.upload(avatar)
        user.avatar = upload_result.get('secure_url')
    db.session.add(user)
    db.session.commit()


def existence_check(attribute ,value):
    return User.query.filter(getattr(User, attribute).__eq__(value)).first()
