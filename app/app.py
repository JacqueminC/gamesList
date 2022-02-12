from glob import escape
import re
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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    form = signinForm()

    if form.validate_on_submit(): 
        print("form validate on submit")
        try:
            if (form.motDePasse.data == form.confMDP.data):
                Player.signin(form)
            else:
                raise Exception("la confirmation du mot de passe n'est pas bonne") 
        except Exception as ex:
            print(ex)
            flash(ex, "error")
            return render_template("signin.html", form=form, ve=ValidationError())

        flash("Inscription réussie!", "signin")        
        return render_template("index.html", )
    
    return render_template("signin.html", form = form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = loginForm()
    return render_template("login.html", form = form)

class signinForm(FlaskForm):
    nom = StringField("Nom", validators=[InputRequired()])
    prenom = StringField("Prénom", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    motDePasse = PasswordField("Mot de passe (6 caractères minimum)", validators=[InputRequired()])
    confMDP = PasswordField("Confirmation du mot de passe", validators=[InputRequired()])

class loginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired()])
    mdp = PasswordField("Mot de passe", validators=[InputRequired()])

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

        if len(motDePasse) >= 6:
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac('sha256', motDePasse.encode('UTF-8'), salt, 100000)
            fullPwd = salt + key

            self.motDePasse = fullPwd.hex()
        else:
           raise Exception("Le motDePasse doit contenir 8 caractère")


    def signin(form):
        print("sign in")
        try:
            player = Player(
                form.nom.data,
                form.prenom.data,
                form.email.data,
                form.motDePasse.data
                )

            Player.savePlayer(player)
        except Exception as ex:
            print(ex)
            raise ex

        

    def savePlayer(player):
        print("save player")
        query = {
            "email" : player.email
        }

        result = playerColl.count_documents(query)
        print("find if email exist => ", result)
        if (result == 0):
            playerColl.insert_one(player.__dict__)
        else:
            raise Exception("Cet email est déjà utilisé")

    def login():
        return "LOGIN"





