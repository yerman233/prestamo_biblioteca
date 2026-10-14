-- ==================== TABLAS ====================

create database biblioteca;

use biblioteca

CREATE TABLE curso (
    id_curso INTEGER PRIMARY KEY AUTO_INCREMENT,
    nivel    TEXT NOT NULL,   --'1° Básico', ..., '8° Básico', 'I Medio', 'II Medio', 'III Medio', 'IV Medio'
    seccion  TEXT NOT NULL,   -- 'A', 'B', 'TP', 'HC'
    UNIQUE (nivel, seccion)
);

CREATE TABLE estudiante (
    id_estudiante INTEGER PRIMARY KEY AUTO_INCREMENT,
    nombre        TEXT NOT NULL,
    id_curso      INTEGER NOT NULL,
    FOREIGN KEY (id_curso) REFERENCES curso(id_curso)
);

CREATE TABLE personal (
    id_personal INTEGER PRIMARY KEY AUTO_INCREMENT,
    nombre      TEXT NOT NULL,
    cargo       TEXT NOT NULL CHECK (cargo IN ('Profesor', 'Funcionario'))
);

CREATE TABLE inventario (
    id_item          INTEGER PRIMARY KEY AUTO_INCREMENT,
    nombre           TEXT NOT NULL,
    tipo             TEXT NOT NULL CHECK (tipo IN ('Proyector', 'Libro', 'Juego', 'Material didáctico')),
    stock_total      INTEGER NOT NULL CHECK (stock_total >= 0),
    stock_disponible INTEGER NOT NULL CHECK (stock_disponible >= 0),
    CHECK (stock_disponible <= stock_total)
);

CREATE TABLE solicitud (
    id_solicitud     INTEGER PRIMARY KEY AUTO_INCREMENT,
    id_estudiante    INTEGER,   -- solo si lo pide un estudiante
    id_personal      INTEGER,   -- solo si lo pide un profesor/funcionario
    id_item          INTEGER NOT NULL,
    cantidad         INTEGER NOT NULL DEFAULT 1,
    fecha_solicitud  TEXT NOT NULL DEFAULT (datetime('now')),
    fecha_devolucion TEXT,      -- NULL = pendiente de devolución
    estado           TEXT NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Devuelto')),
    FOREIGN KEY (id_estudiante) REFERENCES estudiante(id_estudiante),
    FOREIGN KEY (id_personal)   REFERENCES personal(id_personal),
    FOREIGN KEY (id_item)       REFERENCES inventario(id_item),
    CHECK ((id_estudiante IS NULL) <> (id_personal IS NULL))
);

-- ==================== DATOS: INVENTARIO ====================

INSERT INTO inventario (id_item, nombre, tipo, stock_total, stock_disponible) VALUES
-- Proyectores
(1,  'Proyector Epson',                      'Proyector', 4,  4),
(2,  'Proyector portátil BenQ',              'Proyector', 2,  2),

-- Libros
(10, 'Don Quijote de la Mancha',             'Libro', 12, 12),
(11, 'Diccionario de la lengua española',    'Libro', 8,  8),
(12, 'Atlas geográfico escolar',             'Libro', 6,  6),
(13, 'Cuentos de Hans Christian Andersen',   'Libro', 10, 10),

-- Juegos
(20, 'Ajedrez',                              'Juego', 6,  6),
(21, 'Dominó',                               'Juego', 5,  5),
(22, 'Naipe inglés',                         'Juego', 8,  8),
(23, 'Rompecabezas 500 piezas',              'Juego', 4,  4),

-- Material didáctico
(30, 'Set de figuras geométricas',           'Material didáctico', 5,  5),
(31, 'Mapa mural de Chile',                  'Material didáctico', 3,  3),
(32, 'Kit de ciencias (lupa y microscopio)', 'Material didáctico', 4,  4),
(33, 'Ábaco',                                'Material didáctico', 6,  6);