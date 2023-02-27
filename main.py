from flask import Flask, render_template, redirect, url_for, flash, request
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from bonus_functions import send_mail, generate_password

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['TEMPLATES_FOLDER'] = 'templates'
app.config['SECRET_KEY'] = "top_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class login_form(FlaskForm):
    name = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Login")

class register_form(FlaskForm):
    name = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    email = EmailField(label="Email", validators=[DataRequired()])
    submit = SubmitField(label="Login")

class retrive_form(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)

class List(db.Model):
    __tablename__ = "Todo list"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String)
    priority = db.Column(db.String)
    task = db.Column(db.String)
    location = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

with app.app_context():
    db.create_all()
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    db.session.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/list")
def list():
    return render_template("list.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    form = login_form()
    if form.validate_on_submit():
        name = form.name.data
        try:
            user = User.query.filter_by(name=name).first()
            password_check = check_password_hash(user.password, form.password.data)
            if user and password_check:
                login_user(user)
                return redirect('/todo')
            elif user:
                flash("Incorrect password, try again.")
                return redirect(url_for("login"))
        except AttributeError:
            flash("User with this name doesn't exist.")
            return redirect(url_for('login'))

    return render_template("login.html", form=form)

@app.route("/register", methods=["POST", "GET"])
def register():
    form = register_form()
    if form.validate_on_submit():
        new_user = User(name=form.name.data,
                        password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
                        email=form.email.data)

        if User.query.filter_by(name=form.name.data).first():
            flash("This name already exist, choose another one.")
        elif User.query.filter_by(email=form.email.data).first():
            flash("User with this email already exist, choose another one.")
        else:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('/todo')
    return render_template("register.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/todo", methods=["POST", "GET"])
@login_required
def todo():
    todos = List.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        time = request.form.get("time")
        priority = request.form.get("priority")
        task = request.form.get("task")
        location = request.form.get("location")

        new_list = List(time=time, priority=priority, task=task, location=location, user_id=current_user.id)
        db.session.add(new_list)
        db.session.commit()
        return redirect("/todo")
    return render_template("todo.html", todos=todos)

@app.route('/delete/<int:id>')
def delete(id):
    todo_to_remove = List.query.get(id)
    if todo_to_remove is not None:
        db.session.delete(todo_to_remove)
        db.session.commit()
    return redirect('/todo')

@app.route("/retrive", methods=["POST", "GET"])
def retrive():
    form = retrive_form()
    if form.validate_on_submit():
        mail = form.email.data
        user = User.query.filter_by(email=mail).first()
        try:
            if user:
                flash("Done! Check your email for new password.")
                password = generate_password()
                send_mail(mail, password)
                user.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                db.session.commit()
            elif not User.query.filter_by(email=mail).first():
                flash("User with this email doesnt exist, please register first.")
                return redirect("login")
        finally:
            return redirect("login")
    return render_template('retrive.html', form=form)








if __name__ == "__main__":
    app.run(debug=True)