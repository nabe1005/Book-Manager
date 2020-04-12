from flask import *
from flask_login import current_user, login_required

import random

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html', title='TOP')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, books=current_user.books, title='プロフィール')
