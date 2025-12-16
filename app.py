import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

APP_NAME = "El Encanto Barbershop"
ADDRESS = "620 Indian Hills Cir, Perris, CA 92570"

# Admin creds (set these on Render as Environment Variables)
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "change-me")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-secret")

DEPOSIT_AMOUNT = int(os.getenv("DEPOSIT_AMOUNT", "10"))  # ALWAYS ON

DB_PATH = os.getenv("DB_PATH", "db.sqlite")

BARBERS = ["Any Available", "Luis", "Carlos", "Miguel"]
SERVICES = ["Haircut", "Hair + Beard", "Design"]

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            barber TEXT NOT NULL,
            service TEXT NOT NULL,
            appt_time TEXT NOT NULL,
            deposit_amount INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# IMPORTANT: initialize DB on import so it works under Gunicorn/Render
init_db()

@app.route("/", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        barber = request.form.get("barber", "").strip()
        service = request.form.get("service", "").strip()
        appt_time = request.form.get("appt_time", "").strip()

        if not (name and phone and barber and service and appt_time):
            flash("Please fill in all fields.", "error")
            return redirect(url_for("book"))

        conn = get_conn()
        conn.execute(
            "INSERT INTO bookings (name, phone, barber, service, appt_time, deposit_amount, created_at) VALUES (?,?,?,?,?,?,?)",
            (name, phone, barber, service, appt_time, DEPOSIT_AMOUNT, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        return redirect(url_for("success"))

    return render_template(
        "book.html",
        app_name=APP_NAME,
        address=ADDRESS,
        deposit=DEPOSIT_AMOUNT,
        barbers=BARBERS,
        services=SERVICES
    )

@app.route("/success")
def success():
    return render_template("success.html", app_name=APP_NAME)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["is_admin"] = True
            return redirect(url_for("admin"))
        flash("Wrong login.", "error")
        return redirect(url_for("admin_login"))
    return render_template("admin_login.html", app_name=APP_NAME)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("book"))

@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    conn = get_conn()
    rows = conn.execute("SELECT * FROM bookings ORDER BY appt_time ASC").fetchall()
    conn.close()
    return render_template("admin.html", app_name=APP_NAME, rows=rows)

@app.route("/health")
def health():
    return {"ok": True}

# For local dev only (Render uses Gunicorn start command)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
