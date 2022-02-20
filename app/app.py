from ast import And
from flask import Flask, render_template, flash, session, redirect, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, ValidationError
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
import os, hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey"
Bootstrap(app)

client = MongoClient('mongodb://localhost:27017/')
db = client["gamesList"]
playerColl = db["player"]
gameColl = db["game"]

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
            flash(ex, "error")
            return render_template("signin.html", form=form, ve=ValidationError())

        flash("Inscription réussie!", "done")        
        return render_template("index.html", )
    
    return render_template("signin.html", form = form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = loginForm()

    if form.validate_on_submit():
        player = Player.login(form.email.data)

        notFind = 


        if  not player is None and Player.verifyPassword(player["motDePasse"], form.mdp.data):
            session["player"] = {
                "id": str(player["_id"]),
                "fullname": player["prenom"] + " " + player["nom"],
                "email": player["email"]
            }
            session["islogged"] = True
            flash("Identification réussie!", "done")
            return render_template("index.html")
        else:
            ex = Exception("email et/ou mot de passe incorrect(s)")
            flash(ex, "error")
            return render_template("login.html", form = form)


    return render_template("login.html", form = form)

@app.route("/logout")
def logout():
    
    session.pop("player", None)
    session["islogged"] = False

    return redirect("/")

@app.route("/addgame", methods=["GET", "POST"])
def addGame():
    form = addGameForm()    
    
    if session["islogged"] != True:
        return render_template("index.html")

    if form.validate_on_submit():
        Game.saveGame(form.name.data)

    games = Game.findGameByPlayerId(session["player"]["id"])
    form.name.data = ""

    return render_template("addgame.html", form=form, games=games)

@app.route("/actiongame", methods=["GET", "POST"])
def action():
    if request.form.get("trash"):
        Game.deleteGame(request.values["trash"])        

    return redirect("/addgame")


@app.route("/showlist")
def showList():
    games = Game.listAllGames()
    return render_template("showlist.html", games=games)


class signinForm(FlaskForm):
    nom = StringField("Nom", validators=[InputRequired()])
    prenom = StringField("Prénom", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    motDePasse = PasswordField("Mot de passe (6 caractères minimum)", validators=[InputRequired()])
    confMDP = PasswordField("Confirmation du mot de passe", validators=[InputRequired()])

class loginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired()])
    mdp = PasswordField("Mot de passe", validators=[InputRequired()])

class addGameForm(FlaskForm):
    name = StringField("", validators=[InputRequired()], render_kw={"placeholder": "JEU"})

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

    def login(email):
        print("login player")
        query = {
            "email" : email
        }

        return playerColl.find_one(query)

    def verifyPassword(hash, clearPwd):
        hashByte = bytes.fromhex(hash)

        salt = hashByte[:32]
        key = hashByte[32:]

        new_key = hashlib.pbkdf2_hmac('sha256', clearPwd.encode('utf-8'), salt, 100000)

        if new_key == key:
            return True
        else:
            return False
        
class Game():

    def findGameByPlayerId(id):
        query = {
            "idPlayer" : ObjectId(id)
        }

        return gameColl.find(query).sort([("name", pymongo.ASCENDING)])

    def saveGame(name):
        query = {
            "idPlayer" : ObjectId(session["player"]["id"]),
            "name" : name,
            "fullname": session["player"]["fullname"]
        }

        gameColl.insert_one(query)

    def deleteGame(id):
        query = {
            "_id": ObjectId(id)
        }

        gameColl.delete_one(query)

    def listAllGames():
        pipeline = [
            { 
            "$group" : {
                "_id" : "$name", 
                "fullname" : {
                    "$push" : "$fullname"
                    }
                }
            },{"$sort": {"_id":1}}
        ]
        return gameColl.aggregate(pipeline)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')