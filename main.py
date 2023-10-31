from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/colab_zoro'
app.config['SECRET_KEY'] = 'secret key'

db = SQLAlchemy(app)


with app.app_context():
    db.create_all()


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    adresse = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    mail = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.id



@app.route("/")
def login():
    return render_template("zoro.html")


@app.route("/choix/")
def choix():
    return render_template("choix.html")


@app.route("/magasin/")
def magasin():
    # magasin = Data.query.filter_by(id=_id).first()
    magasins = Data.query.order_by(Data.id).all()
    return render_template("magasin.html", magasins=magasins)


@app.route("/new_magasin/", methods=['GET', 'POST'])
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
        return redirect('/magasin')


@app.route("/success/")
def success():
    magasins = Data.query.order_by(Data.id).all()
    return render_template("success.html", magasins=magasins)

@app.route("/modifier_mag/")
def modifier_mag():
    return render_template("modifier_mag.html")

@app.route("/modifier_mag/<int:_id>", methods=["POST", "GET"])
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
        return redirect("/success_edit")

    magasin = Data.query.filter_by(id=_id).first()
    return render_template("modifier_mag.html", magasin=magasin)


@app.route("/supp_def/<int:_id>")
def supp_def(_id):
    # magasins = Data.query.order_by(Data.id).all()
    magasin = Data.query.filter_by(id=_id).first()
    db.session.delete(magasin)
    db.session.commit()
    return redirect("/success_supp")


@app.route("/supp_mag/<int:_id>")
def supp_mag(_id):
    magasins = Data.query.order_by(Data.id).all()
    magasin = Data.query.filter_by(id=_id).first()
    # db.session.delete(magasin)
    # db.session.commit()
    return render_template("/supp_mag.html", magasins=magasins)



@app.route("/success_supp/")
def success_sup():
    magasins = Data.query.order_by(Data.id).all()
    # magasin = Data.query.filter_by(id=_id).first()
    # magasins=magasins
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
