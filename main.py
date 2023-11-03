from collections.abc import Mapping, Sequence
import hashlib
from typing import Any
# from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash

import pymysql
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# DATABASE_URL = 'mysql://root:''@localhost/colab_zoro'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/colab_zoro'
app.config['SECRET_KEY'] = 'secret key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()


# ? Création du modèle SQLAlchemy pour les utilisateurs
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password)  # generate_password_hash(password)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # * Create a String
    def __repr__(self):
        return '<Name %r>' % self.username


# def reset_passwords():
#     users = User.query.all()
#     for user in users:
#         user.set_password(user.password)
#     db.session.commit()


# reset_passwords()


# ? Création du modèle SQLAlchemy pour les Magasins


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    adresse = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    mail = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.id


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=4, max=40)])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6, max=50)])
    submit = SubmitField('Connexion')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=4, max=40)])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6, max=50)])
    submit = SubmitField('Inscription')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # hashed_password = bcrypt.generate_password_hash(password)

        # generate_password_hash(
        # password, method='pbkdf2:sha256')

        # ? Vérifier si le nom d'utilisateur est déjà pris
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exit. Please choose another.', 'danger')
            return redirect(url_for('register'))

        # ? Créer un nouvel utilisateur
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)

        try:
            db.session.commit()
            login_user(new_user)
            flash('Registration successful. You are now log in.', 'success')
            return redirect(url_for('choix'))
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)


# ? Route `/login`
@app.route("/", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        print(f"User found: {user}")
        if user and user.verify_password(password):
            login_user(user)
            flash('You are now log in.', 'success')
            return redirect(url_for('choix'))
        else:
            flash(f'Login failed. Check your username: {
                username} and password: {password}.', 'danger')

    return render_template('zoro.html', form=form)


# ? Route `/logout`
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST':
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    return redirect(request.url)


@app.route("/choix/")
@login_required
def choix():
    return render_template("choix.html")  # redirect(url_for("login"))


@app.route("/magasin/")
@login_required
def magasin():
    # magasin = Data.query.filter_by(id=_id).first()
    magasins = Data.query.order_by(Data.id).all()
    return render_template("magasin.html", magasins=magasins)


@app.route("/new_magasin/", methods=['GET', 'POST'])
@login_required
def new_magasin():
    if request.method == 'GET':
        return render_template('new_magasin.html')

    if request.method == 'POST':
        name = request.form.get('name')
        adresse = request.form.get('adresse')
        telephone = request.form.get('telephone')
        mail = request.form.get('mail')
        magasin = Data(name=name, adresse=adresse,
                       telephone=telephone, mail=mail)
        db.session.add(magasin)
        db.session.commit()
        flash(f"Le {name} a été ajouté avec succès", 'success')
        return redirect('/magasin')


@app.route("/success/")
def success():
    magasins = Data.query.order_by(Data.id).all()
    return render_template("success.html", magasins=magasins)


@app.route("/modifier_mag/<int:_id>", methods=["POST", "GET"])
@login_required
def modifier_mag(_id):
    if request.method == 'POST':
        name = request.form["name"]
        adresse = request.form["adresse"]
        telephone = request.form["telephone"]
        mail = request.form["mail"]
        magasin = Data.query.filter_by(id=_id).first()
        magasin.name = name
        magasin.adresse = adresse
        magasin.telephone = telephone
        magasin.mail = mail
        db.session.add(magasin)
        db.session.commit()

        flash(f"Votre magasin {_id} a été modifié avec succès.")
        return redirect("/magasin")

    magasin = Data.query.filter_by(id=_id).first()
    return render_template("modifier_mag.html", magasin=magasin)


@app.route("/supp_def/<int:_id>")
def supp_def(_id):
    # magasins = Data.query.order_by(Data.id).all()
    magasin = Data.query.filter_by(id=_id).first()
    db.session.delete(magasin)
    db.session.commit()

    flash(f"Le magasin{_id} a été supprimé avec succès.")
    return redirect("/magasin")


@app.route("/supp_mag/<int:_id>")
def supp_mag(_id):
    magasin = Data.query.filter_by(id=_id).first()
    # db.session.delete(magasin)
    # db.session.commit()
    return render_template("/supp_mag.html", id_mag=magasin)


@app.route("/success_supp/")
def success_sup():
    magasins = Data.query.order_by(Data.id).all()
    # mag_id = Data.query.filter_by(id=_id).first()
    # flash_id = flash("{}".format(mag_id.id))
    return render_template("success_supp.html", magasins=magasins)


@app.route("/success_edit/")
def success_edit():
    magasins = Data.query.order_by(Data.id).all()
    return render_template("success_edit.html", magasins=magasins)


@app.route("/MSG_success1/")
def MSG_success1():
    return render_template("MSG_success1.html")


@app.route("/produits/")
def produits():
    return render_template("produits.html")


@app.route("/add_prod/")
def add_prod():
    return render_template("add_prod.html")


@app.route("/edit_prod/")
def edit_prod():
    return render_template("edit_prod.html")


@app.route("/supp_prod/")
def supp_prod():
    return render_template("supp_prod.html")


@app.route("/prod_msg_success/")
def prod_msg_success():
    return render_template("prod_msg_success.html")


@app.route("/prod_success/")
def prod_success():
    return render_template("prod_success.html")


@app.route("/prod_success_edit/")
def prod_success_edit():
    return render_template("prod_success_edit.html")


@app.route("/prod_success_supp/")
def prod_success_supp():
    return render_template("prod_success_supp.html")


# c'est pour éviter d'avoir à écrire dans le terminal à chaque fois
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50000, debug=True)
