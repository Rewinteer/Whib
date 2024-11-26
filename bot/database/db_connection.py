from .config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

Base = declarative_base()

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)

ScopedSession = scoped_session(sessionmaker(bind=engine))

def get_session():
    session = ScopedSession()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        ScopedSession.remove()


if __name__ == '__main__':
    print(DATABASE_URL)