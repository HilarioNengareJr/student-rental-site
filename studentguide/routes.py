import os

from flask import render_template, flash, redirect, url_for, request, session, abort
from flask_login import current_user, logout_user, login_user, login_required
from werkzeug.utils import secure_filename

from studentguide import app, bcrypt, db
from studentguide.forms import LoginForm, RegistrationForm, UpdateAccountForm, PostForm, CommentForm
from studentguide.models import User, Post, Comment
from studentguide.utilities import save_picture


def convert_to_str(a_list):
    temp = " "
    return temp.join(a_list)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413


@app.route('/', methods=['GET', 'POST'])
def home():
    page = request.args.get('page', 1, type=int)
    return render_template("home.html", title="Home Page")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,
                    password=hashed_password)
        user.set_username(form.first_name.data, form.last_name.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.profile_image)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


file_urls = []


@app.route('/post/new', methods=['POST', 'GET'])
def upload_file():
    form = PostForm()
    global file_urls
    # set session for image results
    if "file_urls" not in session:
        session['file_urls'] = []
    file_urls = session['file_urls']
    if request.method == 'POST':
        for uploaded_file in request.files.getlist('file'):
            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    return "Invalid Image", 400
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                file_urls.append(filename)
        session['file_urls'] = file_urls
        print(file_urls)

        if form.validate_on_submit():
            _post = Post(image_folder=str(file_urls), location=form.location.data,
                         phone_number=form.phonenum.data,
                         whatsapp=form.whatsapp.data,
                         city=form.city.data, description=form.description.data,
                         author=current_user)
            db.session.add(_post)
            db.session.commit()

            return redirect(url_for('browse'))

    return render_template('upload_file.html', title="Upload", form=form)


@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
def post(post_id):
    form = CommentForm()
    _post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=_post.id).order_by(Comment.timestamp.desc())
    session.pop('file_urls', None)
    if form.validate_on_submit():
        comment = Comment(body=form.comment.data, post=_post, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!')

        return redirect(url_for('post', post_id=_post.id))

    return render_template('post.html', title="Post", post=_post, urls=eval(_post.image_folder), comments=comments,
                           form=form)


@app.route("/browse", methods=['GET', 'POST'])
def browse():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=5,
                                                                error_out=False)
    next_url = url_for('browse', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('browse', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('browse.html', title="Browse For Home", posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    _post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        _post.whatsapp = form.whatsapp.data
        _post.phonenum = form.phonenum.data
        _post.location = form.location.data
        _post.city = form.city.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=_post.id))
    elif request.method == 'GET':
        form.whatsapp.data = _post.whatsapp
        form.phonenum.data = _post.phonenum
        form.location.data = _post.location
        form.city.data = _post.city
    return render_template('upload_file.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    _post = Post.query.get_or_404(post_id)
    if _post.author != current_user:
        abort(403)
    db.session.delete(_post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/about_page')
def about_page():
    return render_template('about.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))
