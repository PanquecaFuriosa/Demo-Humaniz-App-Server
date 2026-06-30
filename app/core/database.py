import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Configuración de SSL para Supabase
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connect_args = {
        "ssl": ssl_context,
        # Desactiva la caché nativa del driver interno asyncpg
        "statement_cache_size": 0 
    }

# Creamos el engine asíncrono
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False,
    prepared_statement_cache_size=0, 
    connect_args=connect_args
)

# Fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session