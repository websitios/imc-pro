# =====================================================
# CONNECTION.PY
# Conexión PostgreSQL
# =====================================================

import os
import streamlit as st

from sqlalchemy import create_engine


# =====================================================
# DATABASE URL
# =====================================================

DATABASE_URL = st.secrets.get(
    "DATABASE_URL",
    os.getenv("DATABASE_URL")
)


# =====================================================
# ENGINE
# =====================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)