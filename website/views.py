from flask import Blueprint,render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from.models import Ideas, Staff, Category, Department, Like


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

    if request.method == 'POST':
        idea_id = request.form['idea_id']
        status = request.form.get('status')
        staff_id = current_user.id
        print("idea: " + idea_id,"status:", status,"staff_id:", staff_id)
        idea = Ideas.query.get(idea_id)
        if status == "1":
            idea.like += 1
            like = Like(idea_id=idea_id, staff_id=staff_id, status=status)
            db.session.add(like)
            db.session.commit()
            flash('Idea liked successfully', category='success')


        elif status == "-1":
            idea.dislike += 1
            dislike = Like(idea_id=idea_id, staff_id=staff_id, status=status)
            db.session.add(dislike)
            db.session.commit()
            flash('Idea disliked successfully', category='success')

        else:
            flash('error', category='danger')

        return redirect(url_for('views.home'))

    return render_template('staff_home.html', ideas=ideas, user=current_user,
                           categories=category_list, departments=department_list)
