from flask import Flask, render_template

app = Flask(__name__)
@app.route("/")
def login():
    return render_template("zoro.html")

@app.route("/choix/")
def choix():
    return render_template("choix.html")

@app.route("/magasin/")
def magasin():
    return render_template("magasin.html")

@app.route("/new_magasin/")
def new_magasin():
    return render_template("new_magasin.html")

@app.route("/success/")
def success():
    return render_template("success.html")

@app.route("/modifier_mag/")
def modifier_mag():
    return render_template("modifier_mag.html")

@app.route("/supp_mag/")
def supp_mag():
    return render_template("supp_mag.html")

@app.route("/success_supp/")
def success_sup():
    return render_template("success_supp.html")

@app.route("/success_edit/")
def success_edit():
    return render_template("success_edit.html")

@app.route("/MSG_success1/")
def MSG_success1():
    return render_template("MSG_success1.html")




# c'est pour éviter d'avoir à écrire dans le terminal à chaque fois
if __name__=='__main__':
    app.run(debug=True)
