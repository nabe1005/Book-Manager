from flask import *
from application.models import User, Book, Category
from application.database import db
from flask_login import login_required, current_user

categories = Blueprint('categories', __name__)


@categories.route('/categories/index')
@login_required
def index():
    categories = current_user.categories
    n = []

    for category in categories:
        n.append(len(category.books))

    return render_template('categories_index.html', categories=categories, n=n, title='カテゴリの一覧')


@categories.route('/categories/register', methods=['GET'])
@login_required
def register():
    return render_template('categories_register.html', title='カテゴリの追加')


@categories.route('/categories/register', methods=['POST'])
@login_required
def register_post():
    name = request.form.get('name')
    new_category = Category(category_name=name, user_id=current_user.id)

    # バリデーション
    if not name:
        flash('カテゴリ名を入力してください')
        return redirect(url_for('categories.register'))
    for category in current_user.categories:
        if category.category_name == name:
            flash('そのカテゴリは既に追加されています')
            return redirect(url_for('categories.register'))

    # insert
    try:
        db.session.add(new_category)
        db.session.commit()
    except Exception:
        db.session.fallback()
    finally:
        db.session.close()

    return redirect(url_for('categories.index'))


@categories.route('/categories/edit/<int:category_id>')
@login_required
def edit(category_id):
    pass


@categories.route('/categories/delete/<int:category_id>')
@login_required
def delete(category_id):
    pass
