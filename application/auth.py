from typing import Text

from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

from application.models import User
from application.database import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET'])
def login():
    next_page = request.args.get("next")

    return render_template('login.html', next_page=next_page, title='ログイン')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    next_page = request.form.get('next')

    # フォームの空欄の確認
    if email == '' or password == '':
        flash('メールアドレスまたはパスワードが入力されていません')
        return redirect(url_for('auth.login'))

    # メールアドレスは6~254文字以内
    if not 6 <= len(email) <= 254:
        flash('有効なメールアドレスを入力してください')
        return redirect(url_for('auth.login'))

    # パスワードの長さは8文字以上
    if not 8 <= len(password):
        flash('パスワードは8文字以上にしてください')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()

    # ユーザー情報の有無の確認
    if not user:
        flash('入力されたメールアドレスが正しくありません')
        return redirect(url_for('auth.login'))

    # パスワードのチェック
    if not check_password_hash(user.password, password):
        flash('入力されたパスワードが正しくありません')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)

    if next_page != 'None':
        return redirect(next_page)

    return redirect(url_for('main.profile'))


@auth.route('/signup', methods=['GET'])
def signup() -> Text:
    return render_template('signup.html', title='新規登録')


@auth.route('/signup', methods=['POST'])
def signup_post() -> Text:
    name = request.form.get('name')
    display_name = request.form.get('display_name')
    email = request.form.get('email')
    password = request.form.get('password')

    # フォームの空欄を確認
    if name == '' or display_name == '' or email == '' or password == '':
        flash('ユーザ名、表示名、メールアドレスまたはパスワードが入力されていません')
        return redirect(url_for('auth.signup'))

    # メールアドレスの重複を確認
    user_by_email = User.query.filter_by(email=email).first()
    if user_by_email:
        flash('このメールアドレスは既に使用されています')
        return redirect(url_for('auth.signup'))

    # ユーザ名の重複を確認
    user_by_name = User.query.filter_by(name=name).first()
    if user_by_name:
        flash('このユーザ名は既に使用されています')
        return redirect(url_for('auth.signup'))

    # ユーザ名は2~15文字以内
    if not 2 <= len(name) <= 15:
        flash('ユーザ名は2~15文字以内にしてください')
        return redirect(url_for('auth.signup'))

    # ユーザ名は英数字のみ
    if name.isalnum() is True:
        name = request.form.get('name').lower()
    else:
        flash('ユーザ名は英数字のみにしてください')
        return redirect(url_for('auth.signup'))

    # 表示名は50文字以内
    if not 1 <= len(display_name) <= 50:
        flash('表示名は50文字以内にしてください')
        return redirect(url_for('auth.signup'))

    # メールアドレスは6~254文字以内
    if not 6 <= len(email) <= 254:
        flash('有効なメールアドレスを入力してください')
        return redirect(url_for('auth.signup'))

    # パスワードの長さは8文字以上
    if not 8 <= len(password):
        flash('パスワードは8文字以上にしてください')
        return redirect(url_for('auth.signup'))

    hashed_password = generate_password_hash(password, method='sha256')

    new_user = User(name=name, display_name=display_name, email=email, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout() -> Text:
    logout_user()
    return redirect(url_for('main.index'))
