import re
from flask import render_template, request, redirect, flash
from app import app, dao, login_manager
from flask_login import login_user, logout_user


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username, password)
        if user:
            login_user(user)
            return redirect('/')

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    regex_username = '^[a-zA-Z0-9]+$'
    error_message = {}
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username_value = request.form.get('username')
        identification_card = request.form.get('identification')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm')
        email_value = request.form.get('email')
        phone_value = request.form.get('phone')

        customer_type = request.form.get('type')
        gender = request.form.get('gender')

        if not (re.fullmatch(r'\d{12}', identification_card) or re.fullmatch(r'\d{9}', identification_card)
                or re.fullmatch(r'[a-z][a-z0-9]{7}', identification_card, re.IGNORECASE)):
            error_message['err_identification_card'] = 'Identification card is invalid.'

        if dao.existence_check('username', username_value):
            error_message['err_username'] = 'Username is already taken.'

        if not re.fullmatch(regex_username, username_value):
            error_message['err_format'] = 'Invalid username. Only letters and numbers'

        if not password.__eq__(confirm_password):
            error_message['err_password'] = 'Password and confirm password do not match.'

        if '@' not in email_value:
            error_message['err_email'] = 'Email is invalid.'
        elif dao.existence_check('email', email_value):
            error_message['err_email'] = 'Email is already taken.'

        if len(phone_value) < 7 or len(phone_value) > 15:
            error_message['err_phone'] = 'Phone number must be between 7-15 digits.'
        elif dao.existence_check('phone', phone_value):
            error_message['err_phone'] = 'Phone number is already taken.'

        if error_message:
            return render_template('register.html', identification_card=identification_card,
                                   error_message=error_message, name=name, username=username_value,
                                   email=email_value
                                   ,phone=phone_value, customer_type=customer_type, gender=gender)
        else:
            data = request.form.copy()
            del data['confirm']
            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)
            flash('Welcome ' + name + ' to Hotel', 'Registered successfully')
            return redirect('/login')

    return render_template('register.html', customer_type='domestic', gender='male')


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/roomdetail')
def roomdetail():
    return render_template('roomdetail.html')


@app.route('/booking')
def booking():
    return render_template('booking.html')


@app.route('/nvxemphong')
def nvxemphong():
    return render_template('nvxemphong.html')


@app.route('/nvbook')
def nvbook():
    return render_template('nvbook.html')


@app.route('/nvcheckin')
def nvcheckin():
    return render_template('nvcheckin.html')


@app.route('/nvcheckout')
def nvcheckout():
    return render_template('nvcheckout.html')


if __name__ == '__main__':
    app.run(debug=True)
