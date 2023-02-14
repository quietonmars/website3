import sqlite3
from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import create_engine, text
from sqlalchemy.exc import DontWrapMixin


from . import db
from .models import Staff, Category, Admin, Settings, Department, Ideas, DepartmentInfo
from collections import defaultdict


conn = sqlite3.connect('database.db')
# conn.execute("PRAGMA busy_timeout = 5000")

auth = Blueprint('auth', __name__)

conn.row_factory = sqlite3.Row


# engine = create_engine('sqlite:///database.db')
# conn = engine.connect()


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


@auth.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@auth.route('/admin-home')
@login_required
def admin_home():
    return render_template("admin_home.html", user=current_user)


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

            department_name = Staff.query.filter_by(id=current_user.id).first().department
            update_department_info(department_name)
            flash('Posted Idea Successfully', category='success')


    return render_template("add_idea.html", categories=categories, user=current_user)


def update_department_info(department_name):
    department = Department.query.filter_by(name=department_name).first()
    department_info = DepartmentInfo.query.filter_by(department_name=department_name).first()
    if department and department_info:
        department_info.number_of_ideas += 1
        db.session.commit()




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
                window.location = '/categories';
            }}
        </script>
    """


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
    query = "SELECT department.name AS department, COUNT(ideas.id) AS Posts FROM department INNER JOIN staff ON " \
            "department.id = staff.department INNER JOIN ideas ON staff.id = ideas.staff_idGROUP BY department.name "

    result = conn.execute(query).fetchall()
    print(result)
    for row in result:
        department = row[0]
        posts = row[1]
        print(f"Department: {department}, Posts: {posts}")

    conn.close()
    if request.method == 'POST':
        Department_name = request.form.get('newdept')
        new_department = Department(name=Department_name)
        db.session.add(new_department)
        db.session.commit()
        flash('New Department Added Successfully', category='success')

    # Render the template, passing in the required data
    return render_template("department.html", user=current_user)


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
