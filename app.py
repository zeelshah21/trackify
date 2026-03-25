from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Get all expenses
    cur.execute("SELECT * FROM expenses")
    data = cur.fetchall()

    # Get total spending
    cur.execute("SELECT SUM(amount) FROM expenses")
    total = cur.fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    return render_template("index.html", expenses=data, total=total)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
            (amount, category, date)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")


# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM expenses WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")


# ANALYTICS
@app.route("/analytics")
def analytics():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_data = cur.fetchall()

    conn.close()

    categories = [row[0] for row in category_data]
    amounts = [row[1] for row in category_data]

    return render_template("analytics.html", categories=categories, amounts=amounts)


if __name__ == "__main__":
    app.run(debug=True)