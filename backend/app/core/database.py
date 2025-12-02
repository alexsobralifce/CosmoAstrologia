from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import time

print("[DATABASE] 🔧 Configurando engine do banco de dados...")
print(f"[DATABASE] 📍 DATABASE_URL: {settings.DATABASE_URL[:50]}...")

# Configure connect_args based on database type
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    print("[DATABASE] 💾 Usando SQLite")
    # SQLite-specific configuration
    # check_same_thread=False permite uso em múltiplas threads
    # timeout aumenta o tempo de espera para locks (30 segundos)
    connect_args = {
        "check_same_thread": False,
        "timeout": 30.0  # 30 segundos de timeout para operações
    }
else:
    print("[DATABASE] 🐘 Usando PostgreSQL")

# For Postgres and other databases, use default connect_args
try:
    print("[DATABASE] 🔌 Criando engine...")
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,  # Verifica conexões antes de usar
        pool_recycle=3600,  # Recicla conexões após 1 hora
    )
    print("[DATABASE] ✅ Engine criado com sucesso")
    
    # Testar conexão
    print("[DATABASE] 🧪 Testando conexão...")
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("[DATABASE] ✅ Conexão testada com sucesso")
except Exception as e:
    print(f"[DATABASE] ❌ ERRO ao criar engine ou testar conexão: {e}")
    import traceback
    print(f"[DATABASE] Traceback: {traceback.format_exc()}")
    raise

# Habilitar WAL mode para SQLite (melhor concorrência)
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Configura SQLite para melhor performance e concorrência."""
        cursor = dbapi_conn.cursor()
        # WAL mode permite leituras simultâneas e melhor performance
        cursor.execute("PRAGMA journal_mode=WAL")
        # Synchronous NORMAL é mais rápido que FULL, mas ainda seguro
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Busy timeout (em milissegundos) - 30 segundos
        cursor.execute("PRAGMA busy_timeout=30000")
        # Cache size para melhor performance
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency para obter sessão do banco de dados.
    Garante que a sessão seja fechada corretamente.
    Faz rollback automático em caso de exceção não tratada.
    """
    db = SessionLocal()
    try:
        yield db
        # Não fazemos commit automático aqui - os endpoints fazem commit manualmente
        # Isso dá mais controle sobre quando commitar
    except Exception:
        db.rollback()  # Rollback em caso de erro não tratado
        raise
    finally:
        db.close()

