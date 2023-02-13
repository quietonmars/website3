from flask import Blueprint,render_template, request
from flask_login import login_required, current_user
from.models import Ideas

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("staff_home.html", user=current_user)