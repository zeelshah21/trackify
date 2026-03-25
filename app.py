from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# -------------------------------
# DATABASE SETUP (WORKS ON RENDER)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# ROUTES
# -------------------------------

@app.route("/")
def index():
    conn = get_db_connection()
    expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY date DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT SUM(amount) FROM expenses"
    ).fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    return render_template("index.html", expenses=expenses, total=total)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
            (amount, category, date),
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/analytics")
def analytics():
    conn = get_db_connection()

    data = conn.execute(
        "SELECT category, SUM(amount) as total FROM expenses GROUP BY category"
    ).fetchall()

    conn.close()

    categories = [row["category"] for row in data]
    amounts = [row["total"] for row in data]

    return render_template(
        "analytics.html",
        categories=categories,
        amounts=amounts
    )


# -------------------------------
# RUN (LOCAL ONLY)
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
