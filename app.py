import os
import sqlite3
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")


def conectar_db():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tablas():
    with conectar_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                escuela TEXT DEFAULT '',
                grado TEXT DEFAULT '',
                puntos INTEGER DEFAULT 0,
                progreso INTEGER DEFAULT 0,
                fecha_registro TEXT
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                actividad TEXT NOT NULL,
                puntos INTEGER DEFAULT 0,
                total INTEGER DEFAULT 0,
                fecha TEXT NOT NULL
            )
        """)


crear_tablas()


def login_requerido(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            flash("Inicia sesión para entrar a esa sección.", "warning")
            return redirect(url_for("login"))
        return funcion(*args, **kwargs)
    return envoltura


@app.route("/")
def index():
    if session.get("usuario"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")
        escuela = request.form.get("escuela", "").strip()
        grado = request.form.get("grado", "").strip()

        if len(usuario) < 3 or len(password) < 6:
            flash("Usa un usuario de 3 caracteres y una contraseña de 6 como mínimo.", "error")
            return render_template("registro.html")

        try:
            with conectar_db() as db:
                db.execute(
                    "INSERT INTO usuarios (usuario, password, escuela, grado, fecha_registro) VALUES (?, ?, ?, ?, ?)",
                    (usuario, generate_password_hash(password), escuela, grado, datetime.now().strftime("%Y-%m-%d"))
                )
            session["usuario"] = usuario
            flash("¡Tu cuenta quedó lista!", "success")
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            flash("Ese nombre de usuario ya existe. Prueba con otro.", "error")
    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")
        with conectar_db() as db:
            cuenta = db.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
        if cuenta and check_password_hash(cuenta["password"], password):
            session["usuario"] = cuenta["usuario"]
            flash("¡Qué bueno verte de nuevo!", "success")
            return redirect(url_for("dashboard"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("index"))


def datos_usuario():
    usuario = session.get("usuario")
    with conectar_db() as db:
        cuenta = db.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
        resultados = db.execute(
            "SELECT COALESCE(SUM(puntos),0) AS puntos, COUNT(*) AS actividades FROM resultados WHERE usuario = ?",
            (usuario,)
        ).fetchone()
    return cuenta, resultados


@app.route("/dashboard")
@login_requerido
def dashboard():
    cuenta, resultados = datos_usuario()
    return render_template("dashboard.html", cuenta=cuenta, resultados=resultados)


@app.route("/lengua")
@login_requerido
def lengua():
    return render_template("lengua.html")


@app.route("/matematicas")
@login_requerido
def matematicas():
    return render_template("matematicas.html")


@app.route("/juegos")
@login_requerido
def juegos():
    return render_template("juegos.html")


@app.route("/videos")
@login_requerido
def videos():
    return render_template("videos.html")


@app.route("/examen")
@login_requerido
def examen():
    return render_template("examen.html")


@app.route("/guardar-resultado", methods=["POST"])
@login_requerido
def guardar_resultado():
    datos = request.get_json(silent=True) or {}
    actividad = str(datos.get("actividad", "Actividad")).strip()[:80]
    puntos = max(0, min(int(datos.get("puntos", 0)), 1000))
    total = max(0, min(int(datos.get("total", 0)), 1000))
    with conectar_db() as db:
        db.execute(
            "INSERT INTO resultados (usuario, actividad, puntos, total, fecha) VALUES (?, ?, ?, ?, ?)",
            (session["usuario"], actividad, puntos, total, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
    return jsonify({"ok": True})


@app.errorhandler(404)
def no_encontrado(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
