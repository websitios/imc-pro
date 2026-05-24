-- =====================================================
-- SCHEMA.SQL
-- PostgreSQL Schema - IMC PRO
-- =====================================================


-- =====================================================
-- TABLA USUARIOS
-- =====================================================

CREATE TABLE IF NOT EXISTS usuarios (

    id SERIAL PRIMARY KEY,

    usuario VARCHAR(100)
    UNIQUE NOT NULL,

    password VARCHAR(255)
    NOT NULL,

    rol VARCHAR(50)
    DEFAULT 'usuario',

    fecha TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- TABLA EVALUACIONES IMC
-- =====================================================

CREATE TABLE IF NOT EXISTS evaluaciones_imc (

    id SERIAL PRIMARY KEY,

    nombre VARCHAR(200)
    NOT NULL,

    edad INTEGER
    NOT NULL,

    sexo VARCHAR(20)
    NOT NULL,

    peso REAL
    NOT NULL,

    talla REAL
    NOT NULL,

    imc REAL
    NOT NULL,

    diagnostico VARCHAR(100)
    NOT NULL,

    fecha TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP
);