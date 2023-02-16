from flask import Blueprint,render_template, request
from flask_login import login_required, current_user
from.models import Ideas, Staff, Category, Department
from flask_paginate import Pagination, get_page_parameter


views = Blueprint('views', __name__)



@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    ideas = Ideas.query.order_by(Ideas.time.desc()).paginate(page=page, per_page=5)
    categories = Category.query.all()
    departments = Department.query.all()
    category_list = {}
    department_list = {}

    for cat in categories:
        category_list[cat.id] = cat.name

    for dep in departments:
        department_list[dep.id] = dep.name
    print(department_list)
    return render_template('staff_home.html', ideas=ideas, user=current_user,
                           categories=category_list, departments=department_list)


