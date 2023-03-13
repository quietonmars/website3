from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Boolean


class Department(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    staff = db.relationship('Staff')
    admin = db.relationship('Admin', backref='department')


    def add_idea(self):
        self.number_of_ideas += 1

    def update_percentage(self, total_ideas):
        self.percentage_of_ideas = (self.number_of_ideas / total_ideas) * 100


class Staff(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    department = db.Column(db.Integer, db.ForeignKey('department.id'))
    nrc = db.Column(db.String(150))
    role = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    phone_no = db.Column(db.String(150), unique=True)
    address = db.Column(db.String(255))
    username = db.Column(db.String(150))
    password = db.Column(db.String(150))
    notification = db.relationship('Notifications')
    idea = db.relationship('Ideas')
    comment = db.relationship('Comments')
    like_dislike_count = db.relationship('Like')


class Category(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    idea = db.relationship('Ideas')
   # idea = db.relationship('Ideas', backref="category")


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    nrc = db.Column(db.String(150))
    type = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    phone_no = db.Column(db.String(150))
    address = db.Column(db.String(255))
    username = db.Column(db.String(150))
    password = db.Column(db.String(150))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    # department = db.relationship('Department')
    status = db.Column(db.String(150))
    notification = db.relationship('Notifications')
    setting = db.relationship('Settings')


# class Admin(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(150))
#     nrc = db.Column(db.String(150))
#     type = db.Column(db.String(150))
#     email = db.Column(db.String(150), unique=True)
#     phone_no = db.Column(db.String(150))
#     address = db.Column(db.String(255))
#     username = db.Column(db.String(150))
#     password = db.Column(db.String(150))
#     notification = db.relationship('Notifications')
#     setting = db.relationship('Settings')


class Notifications(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    email = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    status = db.Column(db.String(30))


class Settings(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    start_date = db.Column(db.DateTime)
    closure_date = db.Column(db.DateTime)
    final_date = db.Column(db.DateTime)
    saved_date = db.Column(db.DateTime) 


class Ideas(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff = db.relationship('Staff', backref='ideas')
    title = db.Column(db.String(150))
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    description = db.Column(db.String(1000))
    document = db.Column(db.String(150), nullable=False)
    anon = db.Column(Boolean, default=False)
    like = db.Column(db.Integer)
    dislike = db.Column(db.Integer)
    view_count = db.Column(db.Integer)
    comment_count = db.Column(db.Integer)
    comment = db.relationship('Comments')
    like_dislike_count = db.relationship('Like')

    #def _repr_(self):
     #   return f'<Ideas "{self.title}" >'


class Comments(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    description = db.Column(db.String(1000))
    anon = db.Column(Boolean, default=False)


class Like(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    status = db.Column(db.Integer)

