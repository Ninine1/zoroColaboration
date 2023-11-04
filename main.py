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

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import inspect

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


class Magasin(db.Model):
    id_magasin = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    adresse = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    mail = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.id


# ? Création du modèle SQLAlchemy pour les Produits
class Produit(db.Model):
    # Colonne d'identifiant unique
    id_produit = db.Column(db.Integer, primary_key=True)

    # Colonne pour le nom du produit
    name = db.Column(db.String(100), nullable=False)

    # Colonne pour la catégorie du produit
    categorie = db.Column(db.String(100), nullable=False)

    # Colonne pour le prix du produit
    prix = db.Column(db.Float, nullable=False)

    # Méthode spéciale pour représenter l'objet sous forme de chaîne
    def __repr__(self):
        return f'<Produit {self.name}>'


# ? Création du modèle SQLAlchemy pour les Ventes
class Vente(db.Model):
    # Colonne d'identifiant unique
    id_vente = db.Column(db.Integer, primary_key=True)

    # Colonne pour la quantité de produit vendue
    quantite_produit = db.Column(db.Integer, nullable=False)

    # Colonne pour le prix total de la vente
    prix_total = db.Column(db.Float, nullable=False)

    # Colonne pour l'ID du produit vendu (clé étrangère)
    id_produit = db.Column(db.Integer, db.ForeignKey(
        'produit.id_produit'), nullable=False)
    # Définir la relation avec le modèle Produit
    produit = relationship('Produit', backref='vente')

    # Colonne pour l'ID du magasin où la vente a eu lieu (clé étrangère)
    id_magasin = db.Column(db.Integer, db.ForeignKey(
        'magasin.id_magasin'), nullable=False)
    # Définir la relation avec le modèle Magasin
    magasin = relationship('Magasin', backref='vente')

    # Méthode spéciale pour représenter l'objet sous forme de chaîne
    def __repr__(self):
        return f'<Vente {self.id_vente}>'


# Inspecteur pour la classe Vente
inspector = inspect(Vente)

# Boucle à travers les colonnes de la table
for column in inspector.columns.values():
    print(f"Colonne: {column.name}")

    # Vérifier si la colonne a des clés étrangères
    if column.foreign_keys:
        print("C'est une clé étrangère.")
    else:
        print("Ce n'est pas une clé étrangère.")


# ! Modéle formulaire login et register
# ? Modèle Login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=4, max=40)])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6, max=50)])
    submit = SubmitField('Connexion')


# ? Modèle Register
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=4, max=40)])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6, max=50)])
    submit = SubmitField('Inscription')


# ! Gestion Back-End des Users
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ? Register user
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

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


# ? Login user
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


# ? Logout user
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
    # redirect(url_for("login"))
    return render_template("choix.html", title="acceuil")


# ! Gestion Back-End des Magasins
# ? Affichage des produits
@app.route("/magasin/")
@login_required
def magasin():
    magasins = Magasin.query.order_by(Magasin.id_magasin).all()
    return render_template("magasin.html", magasins=magasins, title="Magasin")


# ? Ajouter un nouveau magasin
@app.route("/new_magasin/", methods=['GET', 'POST'])
@login_required
def new_magasin():
    if request.method == 'GET':
        return render_template('new_magasin.html', title="new_magasin")

    if request.method == 'POST':
        name = request.form.get('name')
        adresse = request.form.get('adresse')
        telephone = request.form.get('telephone')
        mail = request.form.get('mail')
        magasin = Magasin(name=name, adresse=adresse,
                          telephone=telephone, mail=mail)
        db.session.add(magasin)
        db.session.commit()
        flash(f"Le {name} a été ajouté avec succès", 'success')
        return redirect('/magasin')


# ? Modification des infos du magasin
@app.route("/modifier_mag/<int:_id>", methods=["POST", "GET"])
@login_required
def modifier_mag(_id):
    if request.method == 'POST':
        name = request.form["name"]
        adresse = request.form["adresse"]
        telephone = request.form["telephone"]
        mail = request.form["mail"]
        magasin = Magasin.query.filter_by(id_magasin=_id).first()
        magasin.name = name
        magasin.adresse = adresse
        magasin.telephone = telephone
        magasin.mail = mail
        db.session.add(magasin)
        db.session.commit()

        flash(f"Le magasin n°{_id} a été modifié avec succès.")
        return redirect("/magasin")

    magasin = Magasin.query.filter_by(id_magasin=_id).first()
    return render_template("modifier_mag.html", magasin=magasin, title="modifier_mag")


# ? Récupération de l'ID du magasin à supprimer
@app.route("/supp_mag/<int:_id>")
@login_required
def supp_mag(_id):
    magasin = Magasin.query.filter_by(id_magasin=_id).first()
    return render_template("/supp_mag.html", id_mag=magasin, title="supp_mag")


# ? Suppression du magasin
@app.route("/supp_def/<int:_id>")
@login_required
def supp_def(_id):
    magasin = Magasin.query.filter_by(id_magasin=_id).first()
    db.session.delete(magasin)
    db.session.commit()

    flash(f"Le magasin N°{_id} a été supprimé ave succcès.")
    return redirect("/magasin")


# ! Gestion Back-End des Produits
# ? Affichage des produits
@app.route("/produits/")
@login_required
def produits():
    produits = Produit.query.order_by(Produit.id_produit).all()
    return render_template("produits.html", produits=produits, title="Produit")


# ? Ajouter un nouveau produit
@app.route("/add_prod/", methods=["POST", "GET"])
@login_required
def add_prod():
    if request.method == 'GET':
        return render_template('add_prod.html', title="add_produit")

    if request.method == 'POST':
        name = request.form.get('name')
        categorie = request.form.get('categorie')
        prix = request.form.get('prix')
        produit = Produit(name=name, categorie=categorie,
                          prix=prix)
        db.session.add(produit)
        db.session.commit()
        flash(f"Le {name} a été ajouté avec succès", 'success')
        return redirect('/produits')


# ? # ? Modification des infos du produit
@app.route("/edit_prod/<int:_id>", methods=["POST", "GET"])
@login_required
def edit_prod(_id):
    if request.method == 'POST':
        name = request.form.get('name')
        categorie = request.form.get('categorie')
        prix = request.form.get('prix')
        produit = Produit.query.filter_by(id_produit=_id).first()
        produit.name = name
        produit.categorie = categorie
        produit.prix = prix
        db.session.add(produit)
        db.session.commit()

        flash(f"Le produit n°{_id} a été modifié avec succès.")
        return redirect("/produits")

    produit = Produit.query.filter_by(id_produit=_id).first()
    return render_template("edit_prod.html", produit=produit, title="edit_prod")


# ? Récupération de l'ID du produit à supprimer
@app.route("/supp_prod/<int:_id>")
@login_required
def supp_prod(_id):
    produit = Produit.query.filter_by(id_produit=_id).first()
    return render_template("/supp_prod.html", id_prod=produit, title="supp_prod")


# ? Suppression du produit
@app.route("/supp_def_prod/<int:_id>")
@login_required
def supp_def_prod(_id):
    produit = Produit.query.filter_by(id_produit=_id).first()
    db.session.delete(produit)
    db.session.commit()

    flash(f"Le Produit N°{_id} a été supprimé ave succcès.")
    return redirect("/produits")


# c'est pour éviter d'avoir à écrire dans le terminal à chaque fois
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50000, debug=True)

# ------------------------MAGASIN------------------------------------
# @app.route("/success/")
# def success():
#     magasins = Magasin.query.order_by(Magasin.id).all()
#     return render_template("success.html", magasins=magasins)


# @app.route("/success_supp/")
# def success_sup():
#     magasins = Magasin.query.order_by(Magasin.id).all()
#     # mag_id = Magasin.query.filter_by(id=_id).first()
#     # flash_id = flash("{}".format(mag_id.id))
#     return render_template("success_supp.html", magasins=magasins)


# @app.route("/success_edit/")
# def success_edit():
#     magasins = Magasin.query.order_by(Magasin.id).all()
#     return render_template("success_edit.html", magasins=magasins)

# @app.route("/MSG_success1/")
# def MSG_success1():
#     return render_template("MSG_success1.html")

# -----------------------------PRODUIT------------------------------------------------
# @app.route("/prod_msg_success/")
# def prod_msg_success():
#     return render_template("prod_msg_success.html")


# @app.route("/prod_success/")
# def prod_success():
#     return render_template("prod_success.html")


# @app.route("/prod_success_edit/")
# def prod_success_edit():
#     return render_template("prod_success_edit.html")


# @app.route("/prod_success_supp/")
# def prod_success_supp():
#     return render_template("prod_success_supp.html")
