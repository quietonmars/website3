from flask import Blueprint,render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import db
from.models import Ideas, Staff, Category, Department, Like
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

    return render_template('staff_home.html', ideas=ideas, user=current_user,
                           categories=category_list, departments=department_list)


@views.route('/', methods=['POST', 'GET'])
@login_required
def like():
    if request.method == 'POST':
        idea_id = request.GET.get('idea_id')
        staff_id = request.GET.get('staff_id')
        status = ""

        idea = Post.objects.get(id=idea_id)

        print(idea_id, staff_id, status)
        like = Like.query.filter_by(idea_id=idea.id, staff_id=staff_id).first()
        if not like:
            like = Like(idea_id=idea.id, staff_id=staff_id, status=status)
            db.session.add(like)
            db.session.commit()
        elif like.status == status:
            db.session.delete(like)
            db.session.commit()
        else:
            like.status = status
            db.session.commit()

        like_count = Like.query.filter_by(idea_id=idea.id, status=1).count()
        dislike_count = Like.query.filter_by(idea_id=idea.id, status=-1).count()
        return render_template('staff_home.html', like_count=like_count, dislike_count=dislike_count, user=current_user)

