from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, ValidationError
from pymongo import MongoClient
import os, hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey"
Bootstrap(app)

client = MongoClient('mongodb://localhost:27017/')
db = client["gamesList"]
playerColl = db["player"]

class signinForm(FlaskForm):
    nom = StringField("Nom", validators=[InputRequired()])
    prenom = StringField("Prénom", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    motDePasse = PasswordField("Mot de passe", validators=[InputRequired()])
    confMDP = PasswordField("Confirmation du mot de passe", validators=[InputRequired()])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signin", methods=["GET", "POST"])
def login():
    form = signinForm()

    if form.validate_on_submit(): 
        try:
            Player.signin(form)   
        except Exception as ex:
            flash(ex, "error")
            return render_template("signin.html", form=form, ve=ValidationError())

        flash("done", "signin")        
        return render_template("index.html", )
    
    return render_template("signin.html", form = form)

class Player():
    def __init__(self, nom, prenom, email, motDePasse):
        if len(nom) > 0:
            self.nom = nom
        else:
           raise Exception("Le nom ne doit pas être vide") 

        if len(prenom) > 0:
            self.prenom = prenom
        else:
           raise Exception("Le prenom ne doit pas être vide")

        if len(email) > 0:
            self.email = email
        else:
           raise Exception("Le email ne doit pas être vide")

        if len(motDePasse) > 8:
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac('sha256', motDePasse.encode('UTF-8'), salt, 100000)
            fullPwd = salt + key

            self.motDePasse = fullPwd.hex()
        else:
           raise Exception("Le motDePasse doit contenir 8 caractère")

    def signin(form):
        try:
            player = Player(
                form.nom.data,
                form.prenom.data,
                form.email.data,
                form.motDePasse.data
                )
        except Exception as ex:
            raise ex

    def savePlayer(player):
        playerColl.insert_one(player.__dict__)





