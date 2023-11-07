from flask_bcrypt import Bcrypt
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import pymysql
# import flask._request_ctx_stack


app = Flask(__name__)
bcrypt = Bcrypt(app)


# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/colab_zoro'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'colab_zoro'

mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

# Utilisez un curseur pour exécuter des requêtes SQL
cursor = mysql.cursor()

app.config['SECRET_KEY'] = 'secret key'


# ! Gestion Back-End des Users
# ? Register user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Vérifier si l'utilisateur existe déjà
        select_query = "SELECT id FROM user WHERE username = %s"
        cursor.execute(select_query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash(
                "Cet utilisateur existe déjà. Veuillez choisir un autre nom d'utilisateur.", 'danger')
        else:
            # Hash du mot de passe
            hashed_password = bcrypt.generate_password_hash(
                password)

            # Insertion de l'utilisateur dans la base de données
            insert_query = "INSERT INTO user (username, password_hash) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, hashed_password))
            mysql.commit()

            # Récupérer l'ID de l'utilisateur nouvellement créé
            cursor.execute(
                "SELECT id FROM user WHERE username = %s", (username,))
            user_id = cursor.fetchone()[0]

            # Connecter l'utilisateur en stockant son ID dans la session
            session['user_id'] = user_id

            flash('Inscription réussie! Vous êtes maintenant connecté.', 'success')
            return redirect(url_for('choix'))

    return render_template('register.html')


# ? Login user
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Requête pour récupérer l'utilisateur depuis la base de données
        select_query = "SELECT id, username, password_hash FROM user WHERE username = %s"
        cursor.execute(select_query, (username,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[2], password):
            # Mot de passe correct, enregistrez l'utilisateur dans la session
            session['user_id'] = user[0]
            flash('Connexion réussie!', 'success')
            return redirect(url_for('choix'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", 'danger')
            flash(f'Login failed. Check your username: {
                username} and password: {password}.', 'danger')

    return render_template('zoro.html')


# Route pour la déconnexion
@app.route('/logout')
def logout():

    # Déconnectez l'utilisateur en supprimant son ID de session
    session.pop('user_id', None)
    # Déconnectez l'utilisateur avec Flask-Login
    # logout_user()
    flash('Déconnexion réussie!', 'success')
    return redirect(url_for('login'))
    # return redirect(request.url)


@app.route("/choix/")
def choix():
    return render_template("choix.html", title="acceuil")


# ! Gestion Back-end des Magasins
# ? Affichage des magasins
@app.route("/magasin/")
def magasin():
    cursor.execute("SELECT * FROM Magasin ORDER BY id_magasin")
    data = cursor.fetchall()

    magasins = []
    for item in data:
        magasins.append(item)

    return render_template("magasin.html", magasins=magasins)


# ? Ajouter un nouveau magasin
@app.route("/new_magasin/", methods=['GET', 'POST'])
def new_magasin():
    if request.method == 'GET':
        return render_template('new_magasin.html', title="new_magasin")

    if request.method == 'POST':
        name = request.form.get('name')
        adresse = request.form.get('adresse')
        telephone = request.form.get('telephone')
        mail = request.form.get('mail')

        insert_query = "INSERT INTO magasin (name, adresse, telephone, mail) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (name, adresse, telephone, mail))
        mysql.commit()

        flash(f"Le {name} a été ajouté avec succès", 'success')

        return redirect('/magasin')


# ? Modification des infos du magasin
@app.route("/modifier_mag/<int:_id>", methods=["POST", "GET"])
def modifier_mag(_id):
    if request.method == 'POST':
        name = request.form["name"]
        adresse = request.form["adresse"]
        telephone = request.form["telephone"]
        mail = request.form["mail"]

        # Requête SQL de mise à jour
        update_query = "UPDATE magasin SET name=%s, adresse=%s, telephone=%s, mail=%s WHERE id_magasin=%s"
        cursor.execute(update_query, (name, adresse, telephone, mail, _id))
        mysql.commit()

        flash(f"Le magasin n°{_id} a été modifié avec succès.")
        return redirect("/magasin")

    # Requête SQL de sélection pour récupérer les informations du magasin
    select_query = "SELECT * FROM magasin WHERE id_magasin=%s"
    cursor.execute(select_query, (_id,))
    magasin = cursor.fetchone()

    return render_template("modifier_mag.html", magasin=magasin, title="modifier_mag")


# ? Récupération de l'ID du magasin à supprimer
@app.route("/supp_mag/<int:_id>")
def supp_mag(_id):
    # Requête SQL de sélection pour récupérer les informations du magasin
    select_query = "SELECT * FROM magasin WHERE id_magasin=%s"
    cursor.execute(select_query, (_id,))
    magasin = cursor.fetchone()

    return render_template("/supp_mag.html", magasin=magasin, title="supp_mag")


# ? Suppression du magasin
@app.route("/supp_def_mag/<int:_id>")
def supp_def(_id):
    try:
        # Requête SQL de suppression
        delete_query = "DELETE FROM magasin WHERE id_magasin=%s"
        cursor.execute(delete_query, (_id,))

        # Validation des changements dans la base de données
        mysql.commit()

        flash(f"Le magasin N°{_id} a été supprimé avec succès.")
        return redirect("/magasin")
    except Exception as e:
        # En cas d'erreur, annuler les changements et afficher un message d'erreur
        mysql.rollback()
        flash(f"Erreur lors de la suppression du magasin: {str(e)}", 'error')


# ! Gestion Back-end des Produits
# ? Affichage des produits
@app.route("/produits/")
def produits():
    cursor.execute("SELECT * FROM Produit ORDER BY id_produit")
    data = cursor.fetchall()

    produits = []
    for item in data:
        produits.append(item)

    return render_template("produits.html", produits=produits, title="Produit")


# ? Ajouter un nouveau produit
@app.route("/add_prod/", methods=["POST", "GET"])
def add_prod():
    try:
        if request.method == 'GET':
            return render_template('add_prod.html', title="add_produit")

        if request.method == 'POST':
            name = request.form.get('name')
            categorie = request.form.get('categorie')
            prix = request.form.get('prix')

            # Exécutez la requête SQL pour ajouter un nouveau produit
            insert_query = """
                INSERT INTO Produit (name, categorie, prix)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (name, categorie, prix))
            mysql.commit()

            flash(f"Le {name} a été ajouté avec succès", 'success')
            return redirect('/produits')

    except Exception as e:
        # Gérez les erreurs, par exemple, affichez un message d'erreur
        flash(f"Erreur lors de l'ajout du produit: {str(e)}", 'error')
        return redirect('/produits')


# ? Modifier un nouveau produit
@app.route("/edit_prod/<int:_id>", methods=["POST", "GET"])
def edit_prod(_id):
    if request.method == 'POST':
        name = request.form.get('name')
        categorie = request.form.get('categorie')
        prix = request.form.get('prix')

        # Requête SQL de mise à jour
        update_query = "UPDATE Produit SET name=%s, categorie=%s, prix=%s WHERE id_produit=%s"
        cursor.execute(update_query, (name, categorie, prix, _id))
        mysql.commit()

        flash(f"Le produit n°{_id} a été modifié avec succès.")
        return redirect("/produits")

    # Requête SQL de sélection pour récupérer les informations du magasin
    select_query = "SELECT * FROM Produit WHERE id_produit=%s"
    cursor.execute(select_query, (_id,))
    produit = cursor.fetchone()

    return render_template("edit_prod.html", produit=produit, title="edit_prod")


# ? Récupération de l'ID du produit à supprimer
@app.route("/supp_prod/<int:_id>")
def supp_prod(_id):
    # Requête SQL de sélection pour récupérer les informations du magasin
    select_query = "SELECT * FROM Produit WHERE id_produit=%s"
    cursor.execute(select_query, (_id,))
    produit = cursor.fetchone()

    return render_template("/supp_prod.html", produit=produit, title="supp_mag")


# ? Suppression du produit
@app.route("/supp_def_prod/<int:_id>")
def supp_def_prod(_id):
    try:
        # Requête SQL de suppression
        delete_query = "DELETE FROM Produit WHERE id_produit=%s"
        cursor.execute(delete_query, (_id,))

        # Validation des changements dans la base de données
        mysql.commit()

        flash(f"Le Produit N°{_id} a été supprimé avec succès.")
        return redirect("/produits")
    except Exception as e:
        # En cas d'erreur, annuler les changements et afficher un message d'erreur
        mysql.rollback()
        flash(f"Erreur lors de la suppression du magasin: {str(e)}", 'error')


# ! Gestion Back-end des Ventes
# ? Afficher la page d'enregistrement des ventes
@app.route('/vente/', methods=['GET', 'POST'])
def vente():
    if request.method == 'POST':
        id_magasin = request.form.get('magasin')
        id_produit = request.form.get('produit')
        quantite = int(request.form.get('quantite'))

        # Récupération du prix unitaire depuis la table Produit
        select_produit_query = "SELECT prix FROM Produit WHERE id_produit=%s"
        cursor.execute(select_produit_query, (id_produit,))
        prix_unitaire = cursor.fetchone()[0]
        print(prix_unitaire)

        prix_total = quantite * prix_unitaire

        try:
            # Insertion de la vente dans la table Vente avec les ID du produit et du magasin
            insert_vente_query = "INSERT INTO Vente (id_magasin, id_produit, quantite_produit, prix_total) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_vente_query, (id_magasin,
                           id_produit, quantite, prix_total))
            mysql.commit()

            flash(f"La vente a été enregistrée avec succès. Prix total: {
                  prix_total}", 'success')
            return redirect('/produits_vente')
        except Exception as e:
            # En cas d'erreur, annuler les changements et afficher un message d'erreur
            mysql.rollback()
            flash(f"Erreur lors de l'enregistrement de la vente: {
                  str(e)}", 'error')

    # Remplir les options des Select avec les noms des magasins et des produits
    select_magasin_query = "SELECT id_magasin, name FROM Magasin"
    cursor.execute(select_magasin_query)
    magasins = cursor.fetchall()

    select_produit_query = "SELECT id_produit, name FROM Produit"
    cursor.execute(select_produit_query)
    produits = cursor.fetchall()

    return render_template('vente.html', magasins=magasins, produits=produits)


# ? Route pour récupérer le prix unitaire d'un produit
@app.route('/get_prix_unitaire/<int:id_produit>', methods=['GET'])
def get_prix_unitaire(id_produit):
    select_produit_query = "SELECT prix FROM Produit WHERE id_produit=%s"
    cursor.execute(select_produit_query, (id_produit,))
    prix_unitaire = cursor.fetchone()[0] if cursor.rowcount > 0 else None
    return jsonify({'prix_unitaire': prix_unitaire})


# ? Afficher toutes les ventes
@app.route('/produits_vente/', methods=['GET'])
def produits_vente():
    try:
        # Exécutez la requête SQL pour récupérer les données
        select_query = """
            SELECT p.name, v.id_produit, v.prix_total AS montant_total,
                   v.quantite_produit, v.id_vente
            FROM Vente v
            JOIN Produit p ON v.id_produit = p.id_produit
            ORDER BY v.id_vente
        """
        cursor.execute(select_query)
        results = cursor.fetchall()
        # print(results)

        return render_template('produits_vente.html', results=results)
    except Exception as e:
        # Gérez les erreurs, par exemple, affichez un message d'erreur
        flash(f"Erreur lors de la récupération des données: {str(e)}", 'error')
        return redirect('/')


# ? Modifier les ventes
@app.route('/modifier_vente/<int:_id>', methods=['GET', 'POST'])
def modifier_vente(_id):
    try:
        # Exécutez la requête SQL pour récupérer les détails de la vente
        select_query = """
            SELECT v.id_vente, v.quantite_produit, v.prix_total, p.id_produit, p.prix, m.id_magasin
            FROM Vente v
            JOIN Produit p ON v.id_produit = p.id_produit
            JOIN Magasin m ON v.id_magasin = m.id_magasin
            WHERE v.id_vente = %s
        """
        cursor.execute(select_query, (_id,))
        vente_details = cursor.fetchone()

        if not vente_details:
            flash("La vente spécifiée n'existe pas.", 'danger')
            # Rediriger vers la liste des ventes
            return redirect(url_for('produits_vente'))

        if request.method == 'POST':
            nouvelle_quantite = int(request.form.get('nouvelle_quantite'))
            nouveau_produit = int(request.form.get('produit'))
            nouveau_magasin = int(request.form.get('magasin'))

            # Calcul du nouveau prix total en fonction de la nouvelle quantité et du prix du nouveau produit
            nouveau_prix_total = nouvelle_quantite * vente_details[4]

            print(nouvelle_quantite)
            print(vente_details[4])
            print(nouveau_prix_total)

            # Mise à jour de la vente avec la nouvelle quantité, le nouveau produit et le nouveau magasin
            update_query = """
                UPDATE Vente
                SET quantite_produit = %s, prix_total = %s, id_produit = %s, id_magasin = %s
                WHERE id_vente = %s
            """
            cursor.execute(
                update_query, (nouvelle_quantite, nouveau_prix_total, nouveau_produit, nouveau_magasin, _id))
            mysql.commit()

            flash(f'La vente N°{_id} a été mise à jour.', 'success')
            # Rediriger vers la liste des ventes
            return redirect(url_for('produits_vente'))

        # Fetch the list of products and stores for the dropdowns
        cursor.execute("SELECT id_produit, name FROM Produit")
        produits = cursor.fetchall()

        cursor.execute("SELECT id_magasin, name FROM Magasin")
        magasins = cursor.fetchall()

        return render_template('modifier_vente.html', vente_details=vente_details, produits=produits, magasins=magasins)
    except Exception as e:
        # Gérez les erreurs, par exemple, affichez un message d'erreur
        flash(f"Erreur lors de la modification de la vente: {str(e)}", 'error')
        return redirect(url_for('produits_vente'))


# ? Supprimer les ventes
@app.route("/supprimer_vente/<int:_id>")
def supprimer_vente(_id):
    try:
        # Exécutez la requête SQL pour supprimer la vente
        delete_query = "DELETE FROM Vente WHERE id_vente = %s"
        cursor.execute(delete_query, (_id,))
        mysql.commit()

        flash(f"La Vente N°{_id} a été supprimée avec succès.")
        return redirect("/produits_vente")
    except Exception as e:
        # Gérez les erreurs, par exemple, affichez un message d'erreur
        flash(f"Erreur lors de la suppression de la vente: {str(e)}", 'error')
        return redirect("/produits_vente")


# c'est pour éviter d'avoir à écrire le port dans terminal à chaque fois
if __name__ == '__main__':
    app.run(debug=True, port=50000)
