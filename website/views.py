from flask import Blueprint,render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from.models import Ideas, Staff, Category, Department, Like


views = Blueprint('views', __name__)



@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    # ideas = Ideas.query.order_by(Ideas.time.desc()).paginate(page=page, per_page=5)
    categories = Category.query.all()
    departments = Department.query.all()
    category_list = {}
    department_list = {}

    sort_option = request.args.get('sort', 'most_recent')
    if sort_option == 'most_viewed':
        ideas = Ideas.query.order_by(Ideas.view_count.desc()).paginate(page=page, per_page=5)
    elif sort_option == 'most_liked':
        ideas = Ideas.query.order_by(Ideas.like.desc()).paginate(page=page, per_page=5)
    else:
        ideas = Ideas.query.order_by(Ideas.time.desc()).paginate(page=page, per_page=5)

    likes = Like.query.filter_by(status=1).all()
    dislikes = Like.query.filter_by(status=-1).all()
    like_list = {}
    dislike_list = {}


    for lik in likes:
        like_list[lik.idea_id] = lik.staff_id

    for dislik in dislikes:
        dislike_list[dislik.idea_id] = dislik.staff_id

    for cat in categories:
        category_list[cat.id] = cat.name

    for dep in departments:
        department_list[dep.id] = dep.name

    if request.method == 'POST':
        idea_id = request.form['idea_id']
        status = request.form.get('status')
        staff_id = current_user.id
        idea = Ideas.query.get(idea_id)
        like = Like.query.filter_by(idea_id=idea_id, staff_id=staff_id).first()

        if like:
            # The user has already liked or disliked the idea
            if like.status == 1 and status == '1':
                # The user has already liked the idea and clicks the like button again, so remove the like
                idea.like -= 1
                db.session.delete(like)
                flash('Idea like removed', category='success')
            elif like.status == -1 and status == '-1':
                # The user has already disliked the idea and clicks the dislike button again, so remove the dislike
                idea.dislike -= 1
                db.session.delete(like)
                flash('Idea dislike removed', category='success')
            elif like.status == 1 and status == '-1':
                # The user has already liked the idea and clicks the dislike button, so remove the like and add the dislike
                idea.like -= 1
                idea.dislike += 1
                like.status = -1
                flash('Idea disliked successfully', category='success')
            elif like.status == -1 and status == '1':
                # The user has already disliked the idea and clicks the like button, so remove the dislike and add the like
                idea.dislike -= 1
                idea.like += 1
                like.status = 1
                flash('Idea liked successfully', category='success')
        else:
            # The user has not yet liked or disliked the idea
            if status == '1':
                # The user likes the idea
                idea.like += 1
                like = Like(idea_id=idea_id, staff_id=staff_id, status=1)
                db.session.add(like)
                flash('Idea liked successfully', category='success')
            elif status == '-1':
                # The user dislikes the idea
                idea.dislike += 1
                like = Like(idea_id=idea_id, staff_id=staff_id, status=-1)
                db.session.add(like)
                flash('Idea disliked successfully', category='success')
            else:
                flash('error', category='danger')

        db.session.commit()

        return redirect(url_for('views.home'))

    return render_template('staff_home.html', ideas=ideas, user=current_user,
                           categories=category_list, departments=department_list, like_list=like_list, dislike_list=dislike_list)

