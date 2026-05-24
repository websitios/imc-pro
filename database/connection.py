# =====================================================
# CONNECTION.PY
# PostgreSQL Connection
# =====================================================

from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql+psycopg2://"
    "admin:TU_PASSWORD@"
    "dpg-d89ka3rbc2fs73fan5vg-a.oregon-postgres.render.com/"
    "imc_pro_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)