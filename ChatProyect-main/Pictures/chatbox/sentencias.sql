
CREATE TABLE IF NOT EXISTS carrera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion VARCHAR NOT NULL UNIQUE,
    duracion_semestres INTEGER, -- Nueva columna
    precio_semestre REAL         -- Nueva columna
);

-- Inserta algunas carreras de ejemplo (opcional)
INSERT OR IGNORE INTO carrera (descripcion, duracion_semestres, precio_semestre) VALUES 
    ('Ingeniería de Sistemas', 8, 2500000.00),
    ('Administración de Empresas', 10, 2400000.00),
    ('Comunicación Social', 9, 2300000.00);