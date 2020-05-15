from flask import *
from application.models import User, Book, Category
from application.database import db
from flask_login import login_required, current_user

books = Blueprint('books', __name__)


@books.route('/books/index')
@login_required
def index():
    series_n = Book.query.filter_by(user_id=current_user.id).order_by(Book.series_id.desc()).first().series_id
    series_n += 1
    res = dict()

    # シリーズの分だけ繰り返し
    for i in range(1, series_n):
        books = Book.query.filter_by(series_id=i, user_id=current_user.id).order_by(Book.vol).all()
        display_vol = ''

        # 巻数の表示
        if books[-1].vol != 1:
            display_vol = '持っている：1~'
            for book in books:
                if book.vol != 1:
                    if book.vol != books[-1].vol:
                        if prev_vol + 1 != book.vol:
                            display_vol = display_vol[:-1] + ', ' + str(book.vol) + '~'
                        prev_vol = book.vol
                    else:
                        if prev_vol + 1 != book.vol:
                            display_vol = display_vol[:-1] + ', ' + str(book.vol) + '巻'
                        else:
                            display_vol += str(book.vol) + '巻'
                else:
                    prev_vol = 1

        # カテゴリの取得
        categories = []
        for category in Book.query.filter_by(series_id=i, user_id=current_user.id).order_by(Book.vol).first().categories:
            categories.append(category.category_name)

        book = {i: {'name': book.book_name, 'vol': display_vol, 'categories': categories}}
        res.update(book)

    return render_template('books_index.html', books=current_user.books, res=jsonify(res), title='本の一覧')


@books.route('/books/register', methods=['GET'])
@login_required
def register():
    categories = current_user.categories
    return render_template('books_register.html', categories=categories, title='本の追加')


@books.route('/books/register', methods=['POST'])
def register_post():
    # データ取得
    book_name = request.form.get('name')
    series = request.form.get('series')
    vol = request.form.get('vol')
    # all_vol = request.form.get('all-vol')
    error_flag = True

    # バリデーション
    if book_name == '':
        flash('本のタイトルを入力してください')
        return redirect(url_for('books.register'))
    if series and int(vol) < 2:
        flash('有効な数字を入力してください')
        return redirect(url_for('books.register'))
    for i in range(int(vol)):
        form_name = 'vol' + str(i + 1)
        if request.form.get(form_name):
            error_flag = False
    if error_flag:
        flash('持っていない巻を選択してください')
        return redirect(url_for('books.register'))

    # Bookインスタンスの作成
    new_books = []
    if Book.query.all():
        series_id = Book.query.order_by(Book.series_id.desc()).first().series_id + 1
    else:
        series_id = 1

    if not series:
        if Book.query.filter_by(book_name=book_name, user_id=current_user.id).first():
            flash('既に追加されています')
            return redirect(url_for('books.register'))
        new_book = Book(series_id=series_id, book_name=book_name, vol=1, user_id=current_user.id)
        new_books.append(new_book)
    else:
        for i in range(int(vol)):
            if Book.query.filter_by(book_name=book_name, user_id=current_user.id).first():
                flash('既に追加されています')
                return redirect(url_for('books.register'))
            if request.form.get('vol' + str(i + 1)):
                new_book = Book(series_id=series_id, book_name=book_name, vol=i + 1, user_id=current_user.id)
                new_books.append(new_book)

    # Categoriesの追加
    for category in current_user.categories:
        if request.form.get(str(category.category_id)):
            new_books[0].categories.append(category)

    # insert
    try:
        db.session.add_all(new_books)
        db.session.commit()
    except Exception:
        db.session.fallback()
    finally:
        db.session.close()

    return redirect(url_for('books.index'))


@books.route('/books/edit/<int:series_id>', methods=['GET'])
@login_required
def edit(series_id):
    edit_books = Book.query.filter_by(series_id=series_id, user_id=current_user.id).order_by(Book.vol).all()

    if not edit_books:
        flash('無効なURLです')
        return redirect(url_for('books.index'))

    categories = current_user.categories

    return render_template('books_edit.html',
                           edit_books=edit_books, categories=categories, title='本の編集')


@books.route('/books/edit/<int:series_id>', methods=['POST'])
@login_required
def edit_post(series_id):
    book_name = request.form.get('name')
    vol = request.form.get('vol')

    # バリデーション
    if not book_name:
        flash('本のタイトルを入力してください')
        return redirect(url_for('books.edit', series_id=series_id))

    error_flag = True
    for i in range(1, int(vol) + 1):
        if request.form.get('vol' + str(i)):
            error_flag = False
    if error_flag:
        flash('持っている巻を選択してください')
        return redirect(url_for('books.edit', series_id=series_id))

    # 更新データの用意
    add_books = []
    if len(Book.query.filter_by(series_id=series_id, user_id=current_user.id).all()) > int(vol):
        i_length = len(Book.query.filter_by(series_id=series_id, user_id=current_user.id).all()) + 1
    else:
        i_length = int(vol) + 1

    for i in range(1, i_length):
        if request.form.get('vol' + str(i)) and i <= int(vol):
            if Book.query.filter_by(series_id=series_id, vol=i, user_id=current_user.id).first():
                add_book = Book.query.filter_by(series_id=series_id, vol=i, user_id=current_user.id).first()
                add_book.book_name = book_name
                add_books.append(add_book)
            else:
                add_books.append(Book(book_name=book_name, series_id=series_id, vol=i, user_id=current_user.id))
        else:
            if Book.query.filter_by(series_id=series_id, vol=i, user_id=current_user.id).first():
                Book.query.filter_by(series_id=series_id, vol=i, user_id=current_user.id).delete()

    add_books[0].categories.clear()
    for category in current_user.categories:
        if request.form.get(str(category.category_id)):
            add_books[0].categories.append(category)

    # update & add
    try:
        db.session.add_all(add_books)
        db.session.commit()
    except Exception:
        db.session.fallback()
    finally:
        db.session.close()

    return redirect(url_for('books.index'))


@books.route('/books/delete/<int:series_id>')
@login_required
def delete(series_id):
    delete_books = Book.query.filter_by(series_id=series_id, user_id=current_user.id).all()

    if not delete_books:
        flash('無効なURLです')
        return redirect(url_for('books.index'))

    # delete
    try:
        for book in delete_books:
            db.session.delete(book)
            db.session.commit()
    except Exception:
        db.session.fallback()
    finally:
        db.session.close()

    return redirect(url_for('books.index'))


# # Bookダミーデータ作成
# @books.route('/seed/b')
# def seed_b():
#     for i in range(random.randint(20, 40)):
#         s = ''
#         for j in range(1, 10):
#             s += chr(0x3042 + random.randint(0, 82))
#         latest_vol = random.randint(1, 12)
#
#         for vol in range(1, latest_vol):
#             new_book = Book(book_name=s, vol=vol, user_id=1)
#             c_ids = []
#             if vol == 1:
#                 for d in range(random.randint(1, 3)):
#                     c_n = current_user.categories
#                     c_ids.append(random.randint(1, len(c_n)))
#             for c_id in c_ids:
#                 new_book.categories.append(Category.query.filter_by(category_id=c_id).first())
#
#             try:
#                 db.session.add(new_book)
#                 db.session.commit()
#             except Exception:
#                 db.session.rollback()
#             finally:
#                 db.session.close()
#
#     return redirect(url_for('main.index'))


# Categoryダミーデータ作成
@books.route('/seed/c')
def seed_c():
    f = open('application/cate.txt')
    c = f.readlines()
    f.close()

    new_categories = []

    for category in c:
        new_categories.append(Category(category_name=category, user_id=1))

    try:
        db.session.add_all(new_categories)
        db.session.commit()
    except Exception:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('main.index'))


# Bookリセット
@books.route('/delete/b')
def delete_b():
    try:
        for book in Book.query.all():
            db.session.delete(book)
        db.session.commit()
    except Exception:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('main.index'))


# Categoryリセット
@books.route('/delete/c')
def delete_c():
    try:
        for category in Category.query.all():
            db.session.delete(category)
        db.session.commit()
    except Exception:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('main.index'))
