from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "pk"

@app.route("/")
def mainpage():
    try:
        conn = sqlite3.connect("competetionDB.sqlite")
        cur = conn.cursor()

        cur.execute("SELECT * FROM COMPETETIONS")
        data = cur.fetchall()

        return render_template("mainpage.html", content = data)
    except sqlite3.Error as e:
        cur.close()
        print(e.args)
        return redirect("/")

@app.route("/entries", methods = ["GET", "POST"])
def entries():
    if request.method != 'POST':
        if "user" in session:

            try:
                conn = sqlite3.connect("competetionDB.sqlite")
                cur = conn.cursor()

                cur.execute("SELECT PASSWORD FROM CREDENTIALS WHERE USERNAME = ?", (session["user"],))
                passwd = cur.fetchone()
                
                if passwd[0] == session["password"]:
                    cur.execute("SELECT * FROM COMPETETIONS")
                    data = cur.fetchall()

                    return render_template("detailEntry.html", content = data)
                else:
                    return redirect(url_for("login"))
            except sqlite3.Error as e:
                cur.close()
                print(e.args)
                return redirect("/")
        else:
            return redirect(url_for("login"))

    try:
        data = request.get_json()

        conn = sqlite3.connect("competetionDB.sqlite")
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS "COMPETETIONS" (
                        "ID"	INTEGER,
                        "NAME"	TEXT,
                        "LASTDATE"	DATE,
                        "GFORMLINK"	TEXT,
                        "APPLICATIONLINK"	TEXT,
                        PRIMARY KEY("ID" AUTOINCREMENT)
                    );""")

        cur.execute("DELETE FROM COMPETETIONS")
        for values in data:
            cur.execute("INSERT INTO COMPETETIONS (NAME, LASTDATE, GFORMLINK, APPLICATIONLINK) VALUES (?, ?, ?, ?)",
            (
                values['Competition Name'],
                values['Last Date'],
                values['GoogleForm link'],
                values['Registration link']
            ))

        conn.commit()
        cur.close()
        return "<script> alert('Data Saved Succesfully'); document.location = '/entries'; </script>"
    except sqlite3.Error as e:
        cur.close()
        print(e.args)
        return redirect("/")


@app.route("/delete", methods = ["POST"])
def delete():
    conn = sqlite3.connect("competetionDB.sqlite")
    cur = conn.cursor()

    cur.execute("DELETE FROM COMPETETIONS WHERE ID = ?", (request.form.get('deletebtn'), ))
    conn.commit()
    cur.close()

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
    app.run(debug=True)