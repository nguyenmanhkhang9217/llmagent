import sys
import os
from sqlalchemy_utils import database_exists, create_database
# Add the backend/app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.database import engine, Base

def init_db():
    # engine.connect()
    print(database_exists(engine.url))
    if not database_exists(engine.url):
        print('not extist')
        create_database(engine.url)
    print(Base.metadata)
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

if __name__ == "__main__":
    init_db()