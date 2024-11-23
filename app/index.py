from flask import render_template, request, redirect
from app import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)