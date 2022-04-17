from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "pk"
# Setting up a Database with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DB.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] =  False

db = SQLAlchemy(app) # connecting flask app to database and initializing it

# Creating table in DataBase using SqlAlchemy --> by creating class we can create new table
# It is independent of any sql syntax
class Competetions(db.Model):
    __tablename__ = "COMPETETIONS"
    id_ = db.Column("id_", db.Integer, primary_key=True) # using id_ be 'id' is standard keyword in python
    # By defualt the first integer column which is primary key is set to auto-increment in SQLAlchemy, can override using auto_increment=False
    name = db.Column("NAME", db.String(50))
    lastdate = db.Column("LASTDATE", db.String(11))
    gformlink = db.Column("GFORMLINK", db.String(500))
    registrationlink = db.Column("REGISTRATIONLINK", db.String(500))

    def __init__(self, name, lastdate, gformlink, registrationlink):
        self.name = name
        self.lastdate = lastdate
        self.gformlink = gformlink
        self.registrationlink = registrationlink

class Credentials(db.Model):
    __tablename__ = "CREDENTIALS"
    username = db.Column("USERNAME", db.String(25), primary_key=True)
    password = db.Column("PASSWORD", db.String(50))


@app.route("/")
def mainpage():
    try:
        # quering all data from COMPETETIONS TABLE
        data = Competetions.query.all()
        
        return render_template("mainpage.html", content = data)
    except Exception as e:
        print(e.args)
        return redirect("/")

@app.route("/entries", methods = ["GET", "POST"])
def entries():
    if request.method != 'POST':
        if "user" in session:

            try:
                # WHERE clause in SQL is 'filter_by' in SQLAlchemy, use 'first()' to get only first returned details
                # returns Credentials class object , and attributes can be accessed using dot operator
                passwd = Credentials.query.filter_by(username = session["user"]).first()
                # print(passwd.password)
                
                if passwd.password == session["password"]:
                    data = Competetions.query.all()
                    cdata = []
                    for val in data:
                        cdata.append([val.id_, val.name, val.lastdate, val.gformlink, val.registrationlink])
    
                    return render_template("detailEntry.html", content = cdata)
                else:
                    return redirect(url_for("login"))
            except Exception as e:
                print(e.args)
                return redirect("/")
        else:
            return redirect(url_for("login"))

    try:
        # getting a list of data from front-end using ajax
        data = request.get_json()

        # Deleting all records in the COMPETETIONS TABLE
        Competetions.query.delete()
        db.session.commit() # committing the changes into the database
        # Whenever we alter the records, DO NOT FORGET TO COMMIT CHANGES

        for values in data:
            # creating a Competetions class' object and initializing the values
            c = Competetions( name=values['Competition Name'], 
                              lastdate=values['Last Date'], 
                              gformlink=values['GoogleForm link'],
                              registrationlink=values['Registration link'] )
            # adding the object to DB, i.e inserting the record into the respective table of the database
            db.session.add(c)
            db.session.commit() # commit changes

        return redirect(url_for("entries"))
    except Exception as e:
        print(e.args)
        return redirect("/")


@app.route("/delete", methods = ["POST"])
def delete():
    # Deleting a record from COMPETETIONS TABLE using Competetion class
    Competetions.query.filter_by(id_=request.form.get('deletebtn')).delete()
    db.session.commit()

    return "<script> document.location = '/entries'; </script>"

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method != "POST":
        return render_template("loginPage.html")

    # sessions to store the details of logged in user
    session["user"] = request.form.get("Username")
    session["password"] = request.form.get("Password")

    return redirect(url_for("entries"))

# Flask buit-in 404-error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 400

if __name__ == "__main__":
    db.create_all() # creates a database if it does not exists while running the app
    app.run(debug=True)