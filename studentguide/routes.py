import os
from studentguide import app, bcrypt, db
from werkzeug.utils import secure_filename
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from studentguide.forms import LoginForm, RegistrationForm, UpdateAccountForm, PostForm
from studentguide.models import User, Post
from flask_login import current_user, logout_user, login_user, login_required
from studentguide.utilities import save_picture


# Error handling for large files.
@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413


@app.route('/', methods=['GET', 'POST'])
def home():
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


@app.route('/post/new', methods=['POST', 'GET'])
def upload_file():
    form = PostForm()
    file_urls = list()
    for uploaded_file in request.files.getlist('file'):
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                return "Invalid Image", 400
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

    if form.validate_on_submit():
        _post = Post(location=form.location.data, city=form.city.data, description=form.description.data,
                     author=current_user)
        db.session.add(_post)
        db.session.commit()

        return redirect(url_for('post', post_id=_post.id))

    #  os.listdir() gets the list of files in the upload location and sends it down to the template for rendering.
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('upload_file.html', title="Upload", files=files, form=form)


#  The uploads are saved to a directory outside of the static folder, this route is used to serve them.
@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route('/post/<int:post_id>')
def post(post_id):
    _post = Post.query.get_or_404(post_id)
    return render_template('post.html', title="Explore", post=_post)


@app.route('/about_page')
def about_page():
    return render_template('about.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))
