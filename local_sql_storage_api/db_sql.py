from sqlmodel import create_engine, Session

engine = create_engine(
    "sqlite:///carsharing.db",
    connect_args={"check_same_thread": False},  # Needed for SQLite, necessary because the Fast API runs async
    echo=True  # Log generated SQL, avoid setting it to True for the production
)


def get_session():
    with Session(engine) as session:
        yield session