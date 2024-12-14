from app import db, app
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from app.models import User, Role
from flask_login import current_user, logout_user
from flask import redirect

admin = Admin(app, name='HotelManagementApp', template_mode='bootstrap4')


class MyView(BaseView):
    def __init__(self, *args, **kwargs):
        self._default_view = True
        super(MyView, self).__init__(*args, **kwargs)
        self.admin = Admin()


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.__eq__(Role.ADMIN)


class AnotherView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AnotherView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/login')


class StatsView(AnotherView):
    @expose("/")
    def index(self):

        return self.render('admin/stats.html')


admin.add_view(AuthenticatedView(User, db.session))
admin.add_view(StatsView(name='Thống kê - báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))