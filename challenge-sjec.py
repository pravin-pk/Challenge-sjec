from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "pk"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DB.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] =  False

db = SQLAlchemy(app)

class Competetions(db.Model):
    __tablename__ = "COMPETETIONS"
    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column("NAME", db.String(50))
    lastdate = db.Column("LASTDATE", db.String(11))
    gformlink = db.Column("GFORMLINK", db.String(500))
    registrationlink = db.Column("REGISTRATIONLINK", db.String(500))

class Credentials(db.Model):
    __tablename__ = "CREDENTIALS"
    username = db.Column("USERNAME", db.String(25), primary_key=True)
    password = db.Column("PASSWORD", db.String(50))


@app.route("/")
def mainpage():
    try:
        # conn = sqlite3.connect("competetionDB.sqlite")
        # cur = conn.cursor()

        # cur.execute("SELECT * FROM COMPETETIONS")
        
        data = Competetions.query.all()
        cdata = []
        for entries in data:
            cdata.append([entries.id,entries.name, entries.lastdate, entries.gformlink, entries.registrationlink])

        return render_template("mainpage.html", content = cdata)
    except Exception as e:
        # cur.close()
        print(e.args)
        return redirect("/")

@app.route("/entries", methods = ["GET", "POST"])
def entries():
    if request.method != 'POST':
        if "user" in session:

            try:
                # conn = sqlite3.connect("competetionDB.sqlite")
                # cur = conn.cursor()

                # cur.execute("SELECT PASSWORD FROM CREDENTIALS WHERE USERNAME = ?", (session["user"],))
                # passwd = cur.fetchone()

                passwd = Credentials.query.filter_by(username = session["user"]).first()
                # print(passwd.password)
                
                if passwd.password == session["password"]:
                    # cur.execute("SELECT * FROM COMPETETIONS")
                    # data = cur.fetchall()
                    data = Competetions.query.all()
                    cdata = []
                    for entries in data:
                        cdata.append([entries.id,entries.name, entries.lastdate, entries.gformlink, entries.registrationlink])

                    print(cdata)
                    return render_template("detailEntry.html", content = cdata)
                else:
                    return redirect(url_for("login"))
            except Exception as e:
                # cur.close()
                print(e.args)
                return redirect("/")
        else:
            return redirect(url_for("login"))

    try:
        data = request.get_json()

        # conn = sqlite3.connect("competetionDB.sqlite")
        # cur = conn.cursor()

        # cur.execute("""CREATE TABLE IF NOT EXISTS "COMPETETIONS" (
        #                 "ID"	INTEGER,
        #                 "NAME"	TEXT,
        #                 "LASTDATE"	DATE,
        #                 "GFORMLINK"	TEXT,
        #                 "APPLICATIONLINK"	TEXT,
        #                 PRIMARY KEY("ID" AUTOINCREMENT)
        #             );""")

        # cur.execute("DELETE FROM COMPETETIONS")
        # for values in data:
        #     cur.execute("INSERT INTO COMPETETIONS (NAME, LASTDATE, GFORMLINK, APPLICATIONLINK) VALUES (?, ?, ?, ?)",
        #     (
        #         values['Competition Name'],
        #         values['Last Date'],
        #         values['GoogleForm link'],
        #         values['Registration link']
        #     ))

        # conn.commit()
        # cur.close()

        Competetions.query.delete()
        db.session.commit()

        for values in data:
            c = Competetions( name=values['Competition Name'], 
                              lastdate=values['Last Date'], 
                              gformlink=values['GoogleForm link'],
                              registrationlink=values['Registration link'] )
            db.session.add(c)
            db.session.commit()

        return redirect(url_for("entries"))
    except Exception as e:
        # cur.close()
        print(e.args)
        return redirect("/")


@app.route("/delete", methods = ["POST"])
def delete():
    # conn = sqlite3.connect("competetionDB.sqlite")
    # cur = conn.cursor()

    # cur.execute("DELETE FROM COMPETETIONS WHERE ID = ?", (request.form.get('deletebtn'), ))
    # conn.commit()
    # cur.close()

    Competetions.query.filter_by(id=request.form.get('deletebtn')).delete()
    db.session.commit()

    return "<script> document.location = '/entries'; </script>"

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method != "POST":
        return render_template("loginPage.html")

    session["user"] = request.form.get("Username")
    session["password"] = request.form.get("Password")

    return redirect(url_for("entries"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 400

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)