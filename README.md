# ⚕️ IMC PRO

Sistema profesional de evaluación del Índice de Masa Corporal (IMC) desarrollado con:

- Python
- Streamlit
- PostgreSQL
- SQLAlchemy
- bcrypt
- Plotly

---

# 🚀 Características

✅ Login profesional con contraseña hash  
✅ Registro de usuarios  
✅ PostgreSQL en Render  
✅ Arquitectura modular profesional  
✅ Dashboard moderno  
✅ Cálculo automático IMC  
✅ Diagnóstico nutricional automático  
✅ Estadísticas interactivas  
✅ Exportación CSV  
✅ Compatible con despliegue en Render  

---

# 📁 Estructura del Proyecto

```txt
imc-pro/
│
├── app.py
│
├── database/
│   ├── auth.py
│   ├── connection.py
│   ├── models.py
│   ├── queries.py
│   └── schema.sql
│
├── .streamlit/
│   └── secrets.toml
│
├── style.css
├── requirements.txt
├── README.md
├── .gitignore
└── .gitattributes
```

---

# ⚙️ Instalación

## 1. Clonar repositorio

```bash
git clone https://github.com/TU-USUARIO/imc-pro.git
```

---

## 2. Entrar al proyecto

```bash
cd imc-pro
```

---

## 3. Crear entorno virtual

```bash
python -m venv venv
```

---

## 4. Activar entorno virtual

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# 🐘 PostgreSQL Render

Crear una base de datos PostgreSQL en:

:contentReference[oaicite:0]{index=0}

Copiar la URL externa:

```txt
postgresql://usuario:password@host/database
```

---

# 🔐 Configurar secrets.toml

Archivo:

```txt
.streamlit/secrets.toml
```

Contenido:

```toml
DATABASE_URL = "postgresql://usuario:password@host/database"
```

---

# ▶️ Ejecutar proyecto

```bash
streamlit run app.py
```

---

# 📦 requirements.txt

```txt
streamlit
pandas
plotly
sqlalchemy
psycopg2-binary
bcrypt
```

---

# 🧠 Tecnologías usadas

| Tecnología | Uso |
|---|---|
| Streamlit | Interfaz web |
| PostgreSQL | Base de datos |
| SQLAlchemy | ORM |
| bcrypt | Seguridad |
| Plotly | Estadísticas |
| Render | Hosting cloud |

---

# ☁️ Despliegue en Render

## Crear Web Service

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

# 🔒 Seguridad

El sistema utiliza:

- Hash bcrypt
- PostgreSQL cloud
- SQLAlchemy parametrizado
- Protección contra SQL Injection

---

# 📊 Funciones IMC

- Registro de evaluaciones
- Historial
- Estadísticas
- Dashboard
- Exportación CSV
- Login profesional

---

# 👨‍💻 Autor

**JOSE LUIS QUISPE FLORES**

Proyecto profesional IMC PRO.

---

# 📄 Licencia

MIT License