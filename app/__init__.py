from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/hoteldb?charset=utf8mb4" % quote('123456')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True



db = SQLAlchemy(app)