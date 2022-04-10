from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

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

        try:
            conn = sqlite3.connect("competetionDB.sqlite")
            cur = conn.cursor()

            cur.execute("SELECT * FROM COMPETETIONS")
            data = cur.fetchall()

            return render_template("detailEntry.html", content = data)
        except sqlite3.Error as e:
            cur.close()
            print(e.args)
            return redirect("/")

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
                values['GForm link'],
                values['application link']
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

    cur.execute("DELETE FROM COMPETETIONS WHERE ID = ?", (request.form['deletebtn'], ))
    conn.commit()
    cur.close()

    return "<script> document.location = '/entries'; </script>"

if __name__ == "__main__":
    app.run(debug=True)