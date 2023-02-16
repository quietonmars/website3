import sqlite3
from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import create_engine, text
from sqlalchemy.exc import DontWrapMixin


from . import db
from .models import Staff, Category, Admin, Settings, Department, Ideas
from collections import defaultdict


conn = sqlite3.connect('././instance/database.db',check_same_thread=False)
conn.execute("PRAGMA busy_timeout = 5000")

auth = Blueprint('auth', __name__)

conn.row_factory = sqlite3.Row


engine = create_engine('sqlite:///database.db')
conn = engine.connect()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        staff = Staff.query.filter_by(username=username).first()
        if staff:
            if check_password_hash(staff.password, password):
                flash('Logged In Successfully!', category='success')
                login_user(staff, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password. Please try again.', category='error')
        else:
            flash('Username does not exist', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/@admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()
        if admin:
            if check_password_hash(admin.password, password):
                flash('Logged In Successfully!', category='success')
                login_user(admin, remember=True)
                return redirect(url_for('auth.admin_home'))
            else:
                flash('Incorrect Password. Please try again.', category='error')
        else:
            flash('Username does not exist', category='error')

    return render_template("admin_login.html", user=current_user)


@auth.route('/admin-logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('auth.admin_login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    q = Department.query.all()
    departments = q
    if request.method == 'POST':
        name = request.form.get('name')
        nric = request.form.get('nric')
        dpt = request.form.get('dpt')
        role = request.form.get('role')
        email = request.form.get('email')
        phone_no = request.form.get('phone_no')
        address = request.form.get('address')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        staff = Staff.query.filter_by(email=email).first()
        username_check = Staff.query.filter_by(username=username).first()
        if username_check:
            flash('Username already exists', category='error')
        elif staff:
            flash('Email already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            new_staff = Staff(name=name, department=dpt, nrc=nric, role=role, email=email, phone_no=phone_no,
                              address=address, username=username,
                              password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_staff)
            db.session.commit()
            flash('Account Created Successfully', category='success')
            return redirect(url_for('auth.login'))

    return render_template("sign_up.html", departments=departments, user=current_user)


@auth.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        user = Staff.query.filter_by(id=current_user.id).first()
    return render_template("profile.html",user=current_user)


@auth.route('/admin-home', methods=['GET', 'POST'])
@login_required
def admin_home():
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
    return render_template('admin_home.html', ideas=ideas, user=current_user,
                           categories=category_list, departments=department_list)


@auth.route('/add-idea', methods=['GET', 'POST'])
@login_required
def add_idea():
    q = Category.query.all()
    categories = q

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('desc')
        category = request.form.get('cat')

        file = request.form.get('file')

        anon = request.form.get('anon')
        tnc = request.form.get('tnc')

        current_datetime = datetime.now()
        value = True if anon == 'on' else False

        if len(title) < 1:
            flash('Please Insert Idea Name', category='error')
        elif len(description) < 1:
            flash('Please Insert Description', category='error')
        elif not category:
            flash('Please Select Category', category='error')
        elif not tnc:
            flash('Please Agree to Terms and Conditions to Post Idea', category='error')
        else:
            new_idea = Ideas(staff_id=current_user.id, title=title, category=category, time=current_datetime,
                             description=description, document=file, anon=value, like=0, dislike=0,
                             view_count=0, comment_count=0)
            db.session.add(new_idea)
            db.session.commit()
            flash('Posted Idea Successfully', category='success')


    return render_template("add_idea.html", categories=categories, user=current_user)



@auth.route('/add-new-admin', methods=['GET', 'POST'])
@login_required
def new_admin():
    if request.method == 'POST':
        name = request.form.get('name')
        nric = request.form.get('nrc')
        type = request.form.get('type')
        email = request.form.get('email')
        phone_no = request.form.get('phone')
        address = request.form.get('address')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        email_admin = Admin.query.filter_by(email=email).first()
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            flash('Username already exists.', category='error')
        elif email_admin:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            new_admin = Admin(name=name, nrc=nric, type=type, email=email, phone_no=phone_no, address=address,
                              username=username, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_admin)
            db.session.commit()

            flash('Admin Account Created Successfully', category='success')
            return redirect(url_for('auth.manage_admin'))
    return render_template("new_admin.html", user=current_user)



@auth.route('/manage-admin')
@login_required
def manage_admin():
    q = Admin.query.all()
    admins = q

    return render_template("manage_admin.html", admins=admins, user=current_user)




@auth.route('/manage-staff')
@login_required
def manage_staff():
    q = Staff.query.all()
    staffs = q

    return render_template("manage_staff.html", staffs=staffs, user=current_user)



@auth.route('/category', methods=['GET', 'POST'])
@login_required
def category():
    q = Category.query.all()
    categories = q

    if request.method == 'POST':
        Category_name = request.form.get('newcat')
        new_category = Category(name=Category_name)
        db.session.add(new_category)
        db.session.commit()
        flash('New Category Added Successfully', category='success')

    return render_template("category.html", category=category, categories=categories,
                           user=current_user)


@auth.route('/delete_category/<int:id>')
def delete_category(id):
    category = Category.query.get_or_404(id)

    return f"""
        <script>
            if (confirm('Are you sure you want to delete the category: {category.name}?')) {{
                window.location = '/delete_category/{category.id}/confirmed';
            }} else {{
                window.location = '/delete_category/{category.id}/cancel';
            }}
        </script>
    """

@auth.route('/delete_category/<int:id>/cancel')
def delete_category_cancel(id):
    flash('Deletion canceled', category='info')
    return redirect(url_for('auth.category'))


@auth.route('/delete_category/<int:id>/confirmed')
def delete_category_confirmed(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Category Deleted', category='success')
    return redirect(url_for('auth.category'))

@auth.route('/department', methods=['GET', 'POST'])
@login_required
def department():
    # query = "SELECT department.name AS department, COUNT(ideas.id) AS Posts FROM department INNER JOIN staff ON " \
    #         "department.id = staff.department INNER JOIN ideas ON staff.id = ideas.staff_id GROUP BY department.name "
    departments = Department.query.all()

    staffs = Staff.query.all()

    department_idea_count = {}
    department_staff_count = {}

    for department in departments:
        department_idea_count[department.id] = 0
        for staff in department.staff:
            department_idea_count[department.id] += len(staff.idea)
        department_staff_count[department.id] = len(department.staff)

    print(department_staff_count, end="Staff count")

    total_idea_count = sum(department_idea_count.values())
    department_idea_percentage = {}

    for department, idea_count in department_idea_count.items():
        department_idea_percentage[department]= 0
        if total_idea_count != 0:
            department_idea_percentage[department] = round((idea_count / total_idea_count) * 100, 2)

    # result = Department.query.all()
    # print(result)
    # for row in result:
    #     department = row[0]
    #     posts = row[1]
    #     print(f"Department: {department}, Posts: {posts}")
    #
    # conn.close()
    if request.method == 'POST':
        Department_name = request.form.get('newdept')
        new_department = Department(name=Department_name)
        db.session.add(new_department)
        db.session.commit()
        flash('New Department Added Successfully', category='success')

    # Render the template, passing in the required data
    return render_template("department.html", user=current_user, departments=departments, department_idea_count=department_idea_count, department_idea_percentage=department_idea_percentage, department_staff_count=department_staff_count)


report_header = (
    "Idea No#", "Posted By", "ID", "Idea Title", "Description", "Category", "Document", "Department", "Date of Post")
report_value = (
    ("1", "John", "123a/t", "Toilet water not working", "the toilet water stops working", "Bug", "11.jpg", "BA",
     "12.Feb.2022"),
    ("2", "Tyler", "124b/t", "Laptop needs upgrade", "my laptop is old and need new one", "Enhancement", "aa.jpg",
     "Developer", "15.July.2022")
)


@auth.route('/manage-ideas')
@login_required
def manage_ideas():
    return render_template("manage_ideas.html", report_value=report_value, report_header=report_header, user=current_user)



@auth.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    q = Settings.query.all()
    settings = q

    for setting in settings:
        setting.admin = Admin.query.get(setting.admin_id)
    if request.method == 'POST':
        s_date = datetime.strptime(request.form.get('start_d'), '%Y-%m-%d')
        e_date = datetime.strptime(request.form.get('new_closure_d'), '%Y-%m-%d')
        fc_date = datetime.strptime(request.form.get('final_closure_d'), '%Y-%m-%d')
        current_date = datetime.now()

        if e_date <= s_date or fc_date <= s_date:
            flash('Start date must be earlier than the closure dates', category='error')
        else:
            new_setting = Settings(admin_id=current_user.id, start_date=s_date, closure_date=e_date, final_date=fc_date,
                               saved_date=current_date)
            db.session.add(new_setting)
            db.session.commit()
            flash('Settings Saved Successfully', category='success')

    return render_template("setting.html", settings=settings, user=current_user)
