import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "cambia-esta-clave"
DATABASE = "biblioteca.db"


# ---------- Conexión a la base de datos ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row          # permite usar fila["nombre"]
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.cli.command("init-db")
def init_db():
    """Crea las tablas leyendo schema.sql"""
    db = get_db()
    with app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
    print("Base de datos creada.")


# ---------- Rutas ----------
@app.route("/")
def index():
    """Panel principal: devoluciones pendientes."""
    pendientes = get_db().execute("""
        SELECT s.id_solicitud, s.cantidad, s.fecha_solicitud,
               i.nombre AS item, i.tipo,
               COALESCE(e.nombre, p.nombre) AS solicitante,
               CASE WHEN e.id_estudiante IS NOT NULL
                    THEN 'Estudiante' ELSE p.cargo END AS rol,
               c.nivel || ' ' || c.seccion AS curso
        FROM solicitud s
        JOIN inventario i       ON i.id_item = s.id_item
        LEFT JOIN estudiante e  ON e.id_estudiante = s.id_estudiante
        LEFT JOIN curso c       ON c.id_curso = e.id_curso
        LEFT JOIN personal p    ON p.id_personal = s.id_personal
        WHERE s.estado = 'Pendiente'
        ORDER BY s.fecha_solicitud
    """).fetchall()
    return render_template("index.html", pendientes=pendientes)


@app.route("/nueva", methods=["GET", "POST"])
def nueva():
    db = get_db()

    if request.method == "POST":
        solicitante = request.form["solicitante"]      # ej: "e-12" o "p-3"
        id_item = int(request.form["id_item"])
        cantidad = int(request.form["cantidad"])
        tipo, id_persona = solicitante.split("-")
        id_estudiante = int(id_persona) if tipo == "e" else None
        id_personal = int(id_persona) if tipo == "p" else None

        # Resta stock solo si alcanza (evita prestar lo que no hay)
        cur = db.execute("""
            UPDATE inventario
            SET stock_disponible = stock_disponible - ?
            WHERE id_item = ? AND stock_disponible >= ?
        """, (cantidad, id_item, cantidad))

        if cur.rowcount == 0:
            db.rollback()
            flash("No hay stock suficiente de ese artículo.")
        else:
            db.execute("""
                INSERT INTO solicitud (id_estudiante, id_personal, id_item, cantidad)
                VALUES (?, ?, ?, ?)
            """, (id_estudiante, id_personal, id_item, cantidad))
            db.commit()
            flash("Solicitud registrada.")
            return redirect(url_for("index"))

    estudiantes = db.execute("""
        SELECT e.id_estudiante, e.nombre, c.nivel || ' ' || c.seccion AS curso
        FROM estudiante e JOIN curso c ON c.id_curso = e.id_curso
        ORDER BY c.id_curso, e.nombre
    """).fetchall()
    personal = db.execute("SELECT * FROM personal ORDER BY nombre").fetchall()
    items = db.execute(
        "SELECT * FROM inventario WHERE stock_disponible > 0 ORDER BY tipo, nombre"
    ).fetchall()
    return render_template("nueva.html", estudiantes=estudiantes,
                           personal=personal, items=items)


@app.route("/devolver/<int:id_solicitud>", methods=["POST"])
def devolver(id_solicitud):
    db = get_db()
    s = db.execute(
        "SELECT * FROM solicitud WHERE id_solicitud = ? AND estado = 'Pendiente'",
        (id_solicitud,)
    ).fetchone()

    if s:
        db.execute("""
            UPDATE solicitud
            SET estado = 'Devuelto', fecha_devolucion = datetime('now')
            WHERE id_solicitud = ?
        """, (id_solicitud,))
        db.execute("""
            UPDATE inventario SET stock_disponible = stock_disponible + ?
            WHERE id_item = ?
        """, (s["cantidad"], s["id_item"]))
        db.commit()
        flash("Devolución registrada.")
    return redirect(url_for("index"))


@app.route("/inventario")
def inventario():
    items = get_db().execute(
        "SELECT * FROM inventario ORDER BY tipo, nombre"
    ).fetchall()
    return render_template("inventario.html", items=items)


if __name__ == "__main__":
    app.run(debug=True)